
import os

import stripe

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.return_request import ReturnRequest
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.payment import Payment
from app.api.deps import require_roles


router = APIRouter(
    prefix="/admin/returns",
    tags=["Admin Returns"]
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ============================================================
# 1. GET ALL RETURN REQUESTS
# ============================================================

@router.get("/")
def get_all_returns(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "staff"))
):
    returns = (
        db.query(ReturnRequest)
        .order_by(ReturnRequest.created_at.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "order_id": item.order_id,
            "user_id": item.user_id,
            "reason": item.reason,
            "comment": item.comment,
            "status": item.status,
            "created_at": item.created_at,
        }
        for item in returns
    ]


# ============================================================
# 2. GET ONE RETURN REQUEST
# ============================================================

@router.get("/{return_id}")
def get_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "staff"))
):
    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    return {
        "id": return_request.id,
        "order_id": return_request.order_id,
        "user_id": return_request.user_id,
        "reason": return_request.reason,
        "comment": return_request.comment,
        "status": return_request.status,
        "created_at": return_request.created_at,
    }


# ============================================================
# 3. APPROVE RETURN
# ============================================================

@router.post("/{return_id}/approve")
def approve_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "staff"))
):
    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    if return_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending return requests can be approved"
        )

    order = (
        db.query(Order)
        .filter(Order.id == return_request.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.order_status.lower() not in [
        "delivered",
        "return_requested"
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Order cannot be returned. "
                f"Current status: {order.order_status}"
            )
        )

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    if not order_items:
        raise HTTPException(
            status_code=400,
            detail="No items found for this order"
        )

    inventory_updates = []

    for order_item in order_items:

        product = (
            db.query(Product)
            .filter(Product.id == order_item.product_id)
            .first()
        )

        if not product:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail=f"Product {order_item.product_id} not found"
            )

        old_stock = product.stock

        product.stock += order_item.quantity

        inventory_updates.append({
            "product_id": product.id,
            "product_name": product.name,
            "returned_quantity": order_item.quantity,
            "old_stock": old_stock,
            "new_stock": product.stock,
        })

    return_request.status = "approved"

    order.order_status = "returned"

    try:
        db.commit()

        db.refresh(return_request)
        db.refresh(order)

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve return: {str(e)}"
        )

    return {
        "message": "Return request approved successfully",
        "return_id": return_request.id,
        "order_id": order.id,
        "return_status": return_request.status,
        "order_status": order.order_status,
        "inventory_updated": True,
        "inventory": inventory_updates,
        "refund_required": True,
    }


# ============================================================
# 4. REJECT RETURN
# ============================================================

@router.post("/{return_id}/reject")
def reject_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "staff"))
):
    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    if return_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending return requests can be rejected"
        )

    order = (
        db.query(Order)
        .filter(Order.id == return_request.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return_request.status = "rejected"

    order.order_status = "rejected"

    try:
        db.commit()

        db.refresh(return_request)
        db.refresh(order)

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject return: {str(e)}"
        )

    return {
        "message": "Return request rejected",
        "return_id": return_request.id,
        "order_id": order.id,
        "return_status": return_request.status,
        "order_status": order.order_status,
        "inventory_updated": False,
        "refund_processed": False,
    }


# ============================================================
# 5. PROCESS STRIPE REFUND
# ============================================================

@router.post("/{return_id}/refund")
def refund_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "staff"))
):
    # --------------------------------------------------------
    # Stripe configuration
    # --------------------------------------------------------

    if not stripe.api_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe secret key is not configured"
        )

    # --------------------------------------------------------
    # Find return request
    # --------------------------------------------------------

    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    # --------------------------------------------------------
    # Refund only approved returns
    # --------------------------------------------------------

    if return_request.status != "approved":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only approved return requests "
                "can be refunded"
            )
        )

    # --------------------------------------------------------
    # Find order
    # --------------------------------------------------------

    order = (
        db.query(Order)
        .filter(Order.id == return_request.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # --------------------------------------------------------
    # Find payment
    # --------------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .order_by(Payment.id.desc())
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment record not found"
        )

    # --------------------------------------------------------
    # Prevent duplicate refunds
    # --------------------------------------------------------

    if payment.status == "refunded":
        raise HTTPException(
            status_code=400,
            detail="Payment has already been refunded"
        )

    # --------------------------------------------------------
    # Payment must be successful
    # --------------------------------------------------------

    if payment.status != "paid":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Payment cannot be refunded. "
                f"Current payment status: {payment.status}"
            )
        )

    # --------------------------------------------------------
    # Stripe PaymentIntent must exist
    # --------------------------------------------------------

    if not payment.transaction_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe transaction ID is missing. "
                "The payment may not have been completed "
                "through Stripe."
            )
        )

    payment_intent_id = payment.transaction_id

    # --------------------------------------------------------
    # Verify transaction looks like a Stripe PaymentIntent
    # --------------------------------------------------------

    if not payment_intent_id.startswith("pi_"):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Stripe PaymentIntent ID "
                "in payment transaction_id"
            )
        )

    # --------------------------------------------------------
    # Create Stripe refund
    # --------------------------------------------------------

    try:

        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            metadata={
                "order_id": str(order.id),
                "return_id": str(return_request.id),
                "payment_id": str(payment.id),
            }
        )

    except stripe.error.StripeError as e:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Stripe refund failed: {str(e)}"
        )

    # --------------------------------------------------------
    # Update payment
    # --------------------------------------------------------

    payment.status = "refunded"

    # --------------------------------------------------------
    # Update order payment status
    # --------------------------------------------------------

    order.payment_status = "refunded"

    # --------------------------------------------------------
    # Update return status
    # --------------------------------------------------------

    return_request.status = "refunded"

    # --------------------------------------------------------
    # Save database changes
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(payment)
        db.refresh(order)
        db.refresh(return_request)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe refund was created, but the "
                f"database update failed: {str(e)}"
            )
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "Refund completed successfully",

        "return_id": return_request.id,

        "order_id": order.id,

        "payment_id": payment.id,

        "return_status": return_request.status,

        "order_status": order.order_status,

        "payment_status": payment.status,

        "order_payment_status": order.payment_status,

        "stripe_refund_id": refund.id,

        "stripe_payment_intent": payment_intent_id,

        "refund_amount": payment.amount,
    }
