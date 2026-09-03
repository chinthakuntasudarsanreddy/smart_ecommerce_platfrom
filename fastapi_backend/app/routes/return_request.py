
import os
from datetime import datetime, timedelta

import stripe

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import (
    get_current_user,
    require_internal_admin_api_key,
)

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.return_request import ReturnRequest
from app.models.refund import Refund
from app.models.payment import Payment

from app.schemas.return_request import ReturnRequestCreate

from app.services.notification_service import (
    return_approved_notification,
    return_rejected_notification,
    refund_completed_notification,
)


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ============================================================
# CUSTOMER RETURN ROUTER
# ============================================================

router = APIRouter(
    prefix="/orders",
    tags=["Returns"],
)

RETURN_WINDOW_DAYS = 7


# ============================================================
# CUSTOMER REQUEST RETURN
# ============================================================

@router.post("/{order_id}/return")
def request_return(
    order_id: int,
    request: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.order_status.lower() != "delivered":
        raise HTTPException(
            status_code=400,
            detail="Return can only be requested for delivered orders",
        )

    if not order.delivered_at:
        raise HTTPException(
            status_code=400,
            detail="Delivery date is not available",
        )

    return_deadline = (
        order.delivered_at +
        timedelta(days=RETURN_WINDOW_DAYS)
    )

    if datetime.utcnow() > return_deadline:
        raise HTTPException(
            status_code=400,
            detail="Return window has expired",
        )

    existing_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.order_id == order.id,
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Return request already exists",
        )

    return_request = ReturnRequest(
        order_id=order.id,
        user_id=current_user.id,
        reason=request.reason,
        comment=request.comment,
        status="pending",
    )

    db.add(return_request)

    order.order_status = "return_requested"

    try:
        db.commit()
        db.refresh(return_request)

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create return request: {str(e)}",
        )

    return {
        "message": "Return request submitted successfully",
        "return_request": {
            "id": return_request.id,
            "order_id": return_request.order_id,
            "reason": return_request.reason,
            "comment": return_request.comment,
            "status": return_request.status,
            "created_at": return_request.created_at,
        },
        "order_status": order.order_status,
    }


# ============================================================
# ADMIN RETURN ROUTER
# ============================================================

admin_router = APIRouter(
    prefix="/admin/returns",
    tags=["Admin Returns"],
)


# ============================================================
# GET ALL RETURNS
# ============================================================

@admin_router.get("/")
def get_all_return_requests(
    db: Session = Depends(get_db),
    _authorized=Depends(require_internal_admin_api_key),
):
    requests = (
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
        for item in requests
    ]


# ============================================================
# GET SINGLE RETURN
# ============================================================

@admin_router.get("/{return_id}")
def get_return_request(
    return_id: int,
    db: Session = Depends(get_db),
    _authorized=Depends(require_internal_admin_api_key),
):
    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found",
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
# APPROVE RETURN
# ============================================================

@admin_router.post("/{return_id}/approve")
async def approve_return_request(
    return_id: int,
    db: Session = Depends(get_db),
    _authorized=Depends(require_internal_admin_api_key),
):
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
            detail="Return request not found",
        )

    # --------------------------------------------------------
    # Only pending requests can be approved
    # --------------------------------------------------------

    if return_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only pending return requests can be approved. "
                f"Current status: {return_request.status}"
            ),
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
            detail="Order not found",
        )

    # --------------------------------------------------------
    # Validate order status
    # --------------------------------------------------------

    if order.order_status.lower() not in [
        "delivered",
        "return_requested",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Order cannot be returned. "
                f"Current status: {order.order_status}"
            ),
        )

    # --------------------------------------------------------
    # Find order items
    # --------------------------------------------------------

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    if not order_items:
        raise HTTPException(
            status_code=400,
            detail="No order items found for this order",
        )

    # --------------------------------------------------------
    # Restore inventory
    # --------------------------------------------------------

    restored_products = []

    for item in order_items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found",
            )

        old_stock = product.stock

        product.stock += item.quantity

        restored_products.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "quantity_restored": item.quantity,
                "old_stock": old_stock,
                "new_stock": product.stock,
            }
        )

    # --------------------------------------------------------
    # Approve return
    # --------------------------------------------------------

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
            detail=f"Failed to approve return: {str(e)}",
        )

    # --------------------------------------------------------
    # Notification
    # --------------------------------------------------------

    try:
        await return_approved_notification(
            db=db,
            order_id=order.id,
            user_id=order.user_id,
        )

    except Exception as e:
        print(
            f"Return approval notification failed: {e}"
        )

    # --------------------------------------------------------
    # IMPORTANT:
    # Payment is NOT checked here.
    # Stripe refund is NOT performed here.
    # --------------------------------------------------------

    return {
        "message": "Return request approved successfully",

        "return_request": {
            "id": return_request.id,
            "status": return_request.status,
        },

        "order": {
            "id": order.id,
            "status": order.order_status,
        },

        "inventory_updated": True,

        "inventory": restored_products,

        "refund_required": True,

        "next_step": (
            f"POST /admin/returns/{return_request.id}/refund"
        ),
    }


# ============================================================
# REJECT RETURN
# ============================================================

@admin_router.post("/{return_id}/reject")
async def reject_return_request(
    return_id: int,
    db: Session = Depends(get_db),
    _authorized=Depends(require_internal_admin_api_key),
):
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
            detail="Return request not found",
        )

    # --------------------------------------------------------
    # Only pending requests can be rejected
    # --------------------------------------------------------

    if return_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only pending return requests can be rejected. "
                f"Current status: {return_request.status}"
            ),
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
            detail="Order not found",
        )

    # --------------------------------------------------------
    # Reject
    # --------------------------------------------------------

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
            detail=f"Failed to reject return: {str(e)}",
        )

    # --------------------------------------------------------
    # Notification
    # --------------------------------------------------------

    try:
        await return_rejected_notification(
            db=db,
            order_id=order.id,
            user_id=order.user_id,
        )

    except Exception as e:
        print(
            f"Return rejection notification failed: {e}"
        )

    return {
        "message": "Return request rejected successfully",

        "return_request": {
            "id": return_request.id,
            "status": return_request.status,
        },

        "order": {
            "id": order.id,
            "status": order.order_status,
        },

        "inventory_updated": False,

        "refund_processed": False,
    }


# ============================================================
# PROCESS STRIPE REFUND
# ============================================================

@admin_router.post("/{return_id}/refund")
async def refund_return(
    return_id: int,
    db: Session = Depends(get_db),
    _authorized=Depends(require_internal_admin_api_key),
):
    # --------------------------------------------------------
    # Stripe configuration
    # --------------------------------------------------------

    if not stripe.api_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe secret key is not configured",
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
            detail="Return request not found",
        )

    # --------------------------------------------------------
    # Only approved returns can be refunded
    # --------------------------------------------------------

    if return_request.status != "approved":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only approved return requests "
                "can be refunded"
            ),
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
            detail="Order not found",
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
            detail="Payment record not found for this order",
        )

    # --------------------------------------------------------
    # Payment must be paid
    # --------------------------------------------------------

    if payment.status == "refunded":
        raise HTTPException(
            status_code=400,
            detail="Payment has already been refunded",
        )

    if payment.status != "paid":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Payment cannot be refunded. "
                f"Current payment status: {payment.status}"
            ),
        )

    # --------------------------------------------------------
    # Stripe PaymentIntent required
    # --------------------------------------------------------

    if not payment.transaction_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe PaymentIntent ID is missing. "
                "The payment may not have been completed "
                "through Stripe."
            ),
        )

    payment_intent_id = payment.transaction_id

    if not payment_intent_id.startswith("pi_"):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Stripe PaymentIntent ID "
                "in payment transaction_id"
            ),
        )

    # --------------------------------------------------------
    # Find existing refund
    # --------------------------------------------------------

    refund = (
        db.query(Refund)
        .filter(Refund.order_id == order.id)
        .order_by(Refund.id.desc())
        .first()
    )

    if refund and refund.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Refund has already been completed",
        )

    # --------------------------------------------------------
    # Create refund record if necessary
    # --------------------------------------------------------

    if not refund:

        refund = Refund(
            order_id=order.id,
            user_id=order.user_id,
            amount=order.total,
            refund_method="original_payment",
            transaction_id=None,
            status="pending",
        )

        db.add(refund)

        try:
            db.commit()
            db.refresh(refund)

        except Exception as e:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Failed to create refund record: {str(e)}",
            )

    # --------------------------------------------------------
    # Stripe refund
    # --------------------------------------------------------

    try:

        stripe_refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=int(
                round(float(refund.amount) * 100)
            ),
            metadata={
                "order_id": str(order.id),
                "refund_id": str(refund.id),
                "return_request_id": str(return_request.id),
            },
        )

    except stripe.error.StripeError as e:

        refund.status = "failed"

        try:
            db.commit()
        except Exception:
            db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Stripe refund failed: {str(e)}",
        )

    # --------------------------------------------------------
    # Update refund
    # --------------------------------------------------------

    refund.transaction_id = stripe_refund.id
    refund.status = "completed"

    # --------------------------------------------------------
    # Update payment
    # --------------------------------------------------------

    payment.status = "refunded"

    # --------------------------------------------------------
    # Update order
    # --------------------------------------------------------

    order.payment_status = "refunded"
    order.order_status = "refunded"

    # --------------------------------------------------------
    # Update return request
    # --------------------------------------------------------

    return_request.status = "refunded"

    # --------------------------------------------------------
    # Commit
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(refund)
        db.refresh(payment)
        db.refresh(order)
        db.refresh(return_request)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe refund was created, but "
                f"database update failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Refund notification
    # --------------------------------------------------------

    try:

        await refund_completed_notification(
            db=db,
            order_id=order.id,
            user_id=order.user_id,
        )

    except Exception as e:

        print(
            f"Refund completed notification failed: {e}"
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "Refund completed successfully",

        "return_request": {
            "id": return_request.id,
            "status": return_request.status,
        },

        "order": {
            "id": order.id,
            "status": order.order_status,
            "payment_status": order.payment_status,
        },

        "payment": {
            "id": payment.id,
            "status": payment.status,
            "transaction_id": payment.transaction_id,
        },

        "refund": {
            "id": refund.id,
            "amount": refund.amount,
            "status": refund.status,
            "transaction_id": refund.transaction_id,
        },
    }