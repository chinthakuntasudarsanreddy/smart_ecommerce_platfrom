from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.models.return_request import ReturnRequest
from app.schemas.order import (
    OrderResponse,
    ReturnRequestCreate,
    ReturnRequestResponse
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ==============================
# GET MY ORDERS
# ==============================

@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db)
):
    orders = db.query(Order).all()

    return orders


# ==============================
# GET ORDER BY ID
# ==============================

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# ==============================
# CONFIRM ORDER
# ==============================

@router.post("/{order_id}/confirm")
def confirm_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.order_status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be confirmed"
        )

    order.order_status = "confirmed"

    db.commit()
    db.refresh(order)

    return {
        "message": "Order confirmed successfully",
        "order_id": order.id,
        "status": order.order_status
    }


# ==============================
# CANCEL ORDER
# ==============================

@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.order_status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be cancelled"
        )

    order.order_status = "cancelled"

    db.commit()
    db.refresh(order)

    return {
        "message": "Order cancelled successfully",
        "order_id": order.id,
        "status": order.order_status
    }


# ==============================
# RETURN ORDER
# ==============================

@router.post(
    "/{order_id}/return",
    response_model=ReturnRequestResponse
)
def request_return(
    order_id: int,
    request: ReturnRequestCreate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Return only delivered orders
    if order.order_status != "delivered":
        raise HTTPException(
            status_code=400,
            detail="Only delivered orders can be returned"
        )

    # Check existing return request
    existing_request = db.query(ReturnRequest).filter(
        ReturnRequest.order_id == order_id
    ).first()

    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Return request already exists"
        )

    return_request = ReturnRequest(
        order_id=order.id,
        user_id=order.user_id,
        reason=request.reason,
        status="pending"
    )

    db.add(return_request)

    # Update order status
    order.order_status = "return_requested"

    db.commit()
    db.refresh(return_request)

    return return_request