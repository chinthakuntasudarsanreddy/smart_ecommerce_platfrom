from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import stripe

from app.core.database import get_db
from app.core.config import settings

from app.models.return_request import ReturnRequest
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.payment import Payment
from app.models.notification import Notification


router = APIRouter(
    prefix="/admin/returns",
    tags=["Admin Returns"]
)


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

stripe.api_key = settings.stripe_secret_key


# ============================================================
# ADMIN AUTHORIZATION
# ============================================================

def verify_admin():
    """
    Replace this with your existing Auth0/admin dependency
    if you already have one.

    For now, this function is a placeholder.
    """

    return True


# ============================================================
# GET ALL RETURN REQUESTS
# ============================================================

@router.get("")
def get_all_returns(
    db: Session = Depends(get_db),
    admin=Depends(verify_admin)
):
    returns = (
        db.query(ReturnRequest)
        .order_by(ReturnRequest.created_at.desc())
        .all()
    )

    result = []

    for return_request in returns:

        order = (
            db.query(Order)
            .filter(Order.id == return_request.order_id)
            .first()
        )

        result.append({
            "id": return_request.id,
            "order_id": return_request.order_id,
            "user_id": return_request.user_id,
            "reason": return_request.reason,
            "comment": return_request.comment,
            "status": return_request.status,
            "created_at": return_request.created_at,
            "order_status": order.order_status if order else None,
            "payment_status": order.payment_status if order else None
        })

    return {
        "success": True,
        "count": len(result),
        "returns": result
    }


# ============================================================
# APPROVE RETURN
# ============================================================

@router.post("/{return_id}/approve")
def approve_return(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(verify_admin)
):

    # --------------------------------------------------------
    # 1. Find return request
    # --------------------------------------------------------

    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    # --------------------------------------------------------
    # 2. Prevent duplicate processing
    # --------------------------------------------------------

    if return_request.status == "refunded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return has already been refunded"
        )

    if return_request.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return has already been approved"
        )

    if return_request.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejected return cannot be approved"
        )

    if return_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Return cannot be approved from status '{return_request.status}'"
        )

    # --------------------------------------------------------
    # 3. Get order
    # --------------------------------------------------------

    order = (
        db.query(Order)
        .filter(Order.id == return_request.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # --------------------------------------------------------
    # 4. Get order items
    # --------------------------------------------------------

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    if not order_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has no items"
        )

    # --------------------------------------------------------
    # 5. Restore inventory
    # --------------------------------------------------------

    for item in order_items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )

        product.stock += item.quantity

    # --------------------------------------------------------
    # 6. Update return/order status
    # --------------------------------------------------------

    return_request.status = "returned"

    order.order_status = "Returned"

    # --------------------------------------------------------
    # 7. Find payment
    # --------------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .order_by(Payment.id.desc())
        .first()
    )

    if not payment:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found"
        )

    # --------------------------------------------------------
    # 8. Stripe refund
    # --------------------------------------------------------

    if payment.status.lower() == "refunded":
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment has already been refunded"
        )

    if not payment.transaction_id:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe transaction ID is missing"
        )

    if not settings.stripe_secret_key:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe secret key is not configured"
        )

    try:

        refund = stripe.Refund.create(
            payment_intent=payment.transaction_id
        )

    except stripe.error.StripeError as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe refund failed: {str(e)}"
        )

    # --------------------------------------------------------
    # 9. Update payment status
    # --------------------------------------------------------

    payment.status = "refunded"

    order.payment_status = "refunded"

    # --------------------------------------------------------
    # 10. Update return status
    # --------------------------------------------------------

    return_request.status = "refunded"

    # --------------------------------------------------------
    # 11. In-app notification
    # --------------------------------------------------------

    approval_notification = Notification(
        user_id=return_request.user_id,
        order_id=order.id,
        type="return_approved",
        message=(
            f"Your return request for order #{order.id} "
            f"has been approved."
        ),
        read_status=False
    )

    db.add(approval_notification)

    refund_notification = Notification(
        user_id=return_request.user_id,
        order_id=order.id,
        type="refund_completed",
        message=(
            f"Your refund for order #{order.id} "
            f"has been completed successfully."
        ),
        read_status=False
    )

    db.add(refund_notification)

    # --------------------------------------------------------
    # 12. Commit everything
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(return_request)
        db.refresh(order)
        db.refresh(payment)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database update failed: {str(e)}"
        )

    # --------------------------------------------------------
    # 13. Response
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Return approved and refund completed",
        "return_id": return_request.id,
        "return_status": return_request.status,
        "order_id": order.id,
        "order_status": order.order_status,
        "payment_status": payment.status,
        "stripe_refund_id": refund.id
    }


# ============================================================
# REJECT RETURN
# ============================================================

@router.post("/{return_id}/reject")
def reject_return(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(verify_admin)
):

    # --------------------------------------------------------
    # 1. Find return request
    # --------------------------------------------------------

    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    # --------------------------------------------------------
    # 2. Validate status
    # --------------------------------------------------------

    if return_request.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return has already been rejected"
        )

    if return_request.status == "refunded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refunded return cannot be rejected"
        )

    if return_request.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approved return cannot be rejected"
        )

    if return_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Return cannot be rejected from status '{return_request.status}'"
        )

    # --------------------------------------------------------
    # 3. Get order
    # --------------------------------------------------------

    order = (
        db.query(Order)
        .filter(Order.id == return_request.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # --------------------------------------------------------
    # 4. Update status
    # --------------------------------------------------------

    return_request.status = "rejected"

    # Keep original order status.
    # We do NOT change inventory.
    # We do NOT issue a refund.

    # --------------------------------------------------------
    # 5. In-app notification
    # --------------------------------------------------------

    notification = Notification(
        user_id=return_request.user_id,
        order_id=order.id,
        type="return_rejected",
        message=(
            f"Your return request for order #{order.id} "
            f"has been rejected."
        ),
        read_status=False
    )

    db.add(notification)

    # --------------------------------------------------------
    # 6. Commit
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(return_request)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database update failed: {str(e)}"
        )

    # --------------------------------------------------------
    # 7. Response
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Return request rejected",
        "return_id": return_request.id,
        "return_status": return_request.status,
        "order_id": order.id,
        "order_status": order.order_status,
        "payment_status": order.payment_status
    }