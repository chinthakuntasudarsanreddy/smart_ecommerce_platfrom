from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_roles

from app.models.refund import Refund
from app.models.return_request import ReturnRequest
from app.models.order import Order

from app.schemas.refund import (
    RefundCreate,
    RefundStatusUpdate,
    RefundResponse,
)


router = APIRouter(
    prefix="/admin/refunds",
    tags=["Refunds"],
)


# ============================================================
# CREATE REFUND
# ============================================================

@router.post(
    "/",
    response_model=RefundResponse,
)
def create_refund(
    refund_data: RefundCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "staff")
    ),
):

    # Find order
    order = (
        db.query(Order)
        .filter(
            Order.id == refund_data.order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # Check if refund already exists
    existing_refund = (
        db.query(Refund)
        .filter(
            Refund.order_id == refund_data.order_id
        )
        .first()
    )

    if existing_refund:
        raise HTTPException(
            status_code=400,
            detail="Refund already exists for this order",
        )

    # Validate amount
    if refund_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Refund amount must be greater than zero",
        )

    if refund_data.amount > order.total:
        raise HTTPException(
            status_code=400,
            detail="Refund amount cannot exceed order total",
        )

    # Create refund
    refund = Refund(
        order_id=order.id,
        user_id=order.user_id,
        amount=refund_data.amount,
        refund_method=refund_data.refund_method,
        status="pending",
    )

    db.add(refund)

    db.commit()
    db.refresh(refund)

    return refund


# ============================================================
# GET ALL REFUNDS
# ============================================================

@router.get(
    "/",
    response_model=list[RefundResponse],
)
def get_all_refunds(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "staff")
    ),
):

    refunds = (
        db.query(Refund)
        .order_by(
            Refund.created_at.desc()
        )
        .all()
    )

    return refunds


# ============================================================
# GET SINGLE REFUND
# ============================================================

@router.get(
    "/{refund_id}",
    response_model=RefundResponse,
)
def get_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "staff")
    ),
):

    refund = (
        db.query(Refund)
        .filter(
            Refund.id == refund_id
        )
        .first()
    )

    if not refund:
        raise HTTPException(
            status_code=404,
            detail="Refund not found",
        )

    return refund


# ============================================================
# UPDATE REFUND STATUS
# ============================================================

@router.put(
    "/{refund_id}/status",
    response_model=RefundResponse,
)
def update_refund_status(
    refund_id: int,
    status_data: RefundStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "staff")
    ),
):

    refund = (
        db.query(Refund)
        .filter(
            Refund.id == refund_id
        )
        .first()
    )

    if not refund:
        raise HTTPException(
            status_code=404,
            detail="Refund not found",
        )

    new_status = (
        status_data.status
        .lower()
        .strip()
    )

    allowed_statuses = {
        "pending",
        "processing",
        "completed",
        "failed",
        "cancelled",
    }

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid refund status. "
                "Allowed: pending, processing, "
                "completed, failed, cancelled"
            ),
        )

    refund.status = new_status

    db.commit()
    db.refresh(refund)

    return refund