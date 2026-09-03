from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.api.deps import require_internal_admin_api_key


router = APIRouter(
    prefix="/orders",
    tags=["Order Status"]
)


ALLOWED_STATUSES = {
    "pending",
    "paid",
    "shipped",
    "delivered",
    "cancelled",
    "return_requested",
}


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    admin_key=Depends(require_internal_admin_api_key),
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    new_status = new_status.lower().strip()

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order status: {new_status}"
        )

    # Optional lifecycle protection
    valid_transitions = {
        "pending": ["paid", "cancelled"],
        "paid": ["shipped", "cancelled"],
        "shipped": ["delivered", "cancelled"],
        "delivered": ["return_requested"],
        "return_requested": [],
        "cancelled": [],
    }

    current_status = (order.order_status or "pending").lower().strip()

    if current_status != new_status:
        allowed_next_statuses = valid_transitions.get(
            current_status,
            []
        )

        if new_status not in allowed_next_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid status transition: "
                    f"{current_status} -> {new_status}"
                )
            )

    order.order_status = new_status

    # Set delivery timestamp automatically
    if new_status == "delivered":
        order.delivered_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "order_status": order.order_status,
        "delivered_at": order.delivered_at,
    }