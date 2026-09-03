from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.api.deps import require_roles


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "staff"))
):
    # Find order
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Normalize status
    new_status = new_status.lower().strip()

    # Allowed statuses
    allowed_statuses = {
        "pending",
        "paid",
        "shipped",
        "delivered",
        "cancelled",
        "return_requested",
    }

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid status. Allowed values: "
                "pending, paid, shipped, delivered, "
                "cancelled, return_requested"
            )
        )

    # Update status
    order.order_status = new_status

    # If delivered, save delivery date
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