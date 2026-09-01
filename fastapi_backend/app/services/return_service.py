from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.return_request import ReturnRequest


RETURNABLE_ORDER_STATUSES = {
    "delivered"
}


def validate_return_request(
    db: Session,
    order_id: int,
    user_id: int
):
    # 1. Find order
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 2. Check ownership
    if order.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot request a return for this order"
        )

    # 3. Check order status
    if order.order_status not in RETURNABLE_ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Order cannot be returned. "
                f"Current status: {order.order_status}"
            )
        )

    # 4. Check duplicate return request
    existing_return = db.query(ReturnRequest).filter(
        ReturnRequest.order_id == order_id
    ).first()

    if existing_return:
        raise HTTPException(
            status_code=400,
            detail="A return request already exists for this order"
        )

    return order