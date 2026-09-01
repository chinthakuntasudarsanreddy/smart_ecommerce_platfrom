from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.models.return_request import ReturnRequest
from app.schemas.return_request import (
    ReturnRequestCreate,
    ReturnRequestResponse,
)

# Change this import if your project uses a different auth dependency
from app.api.auth import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Returns"]
)


RETURN_WINDOW_DAYS = 7


@router.post(
    "/{order_id}/return",
    response_model=ReturnRequestResponse,
    status_code=status.HTTP_201_CREATED
)
def request_return(
    order_id: int,
    request: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. Find order
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 2. Check order status
    if order.status.lower() != "delivered":
        raise HTTPException(
            status_code=400,
            detail="Return can only be requested for delivered orders"
        )

    # 3. Check delivery date
    delivered_at = getattr(order, "delivered_at", None)

    if not delivered_at:
        raise HTTPException(
            status_code=400,
            detail="Delivery date is not available for this order"
        )

    return_deadline = delivered_at + timedelta(
        days=RETURN_WINDOW_DAYS
    )

    if datetime.utcnow() > return_deadline:
        raise HTTPException(
            status_code=400,
            detail="Return window has expired"
        )

    # 4. Check existing return request
    existing_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.order_id == order.id)
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Return request already exists for this order"
        )

    # 5. Create return request
    return_request = ReturnRequest(
        order_id=order.id,
        user_id=current_user.id,
        reason=request.reason,
        comment=request.comment,
        status="pending"
    )

    db.add(return_request)

    # 6. Update order status
    order.status = "Return Requested"

    db.commit()
    db.refresh(return_request)

    return return_request