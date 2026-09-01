
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.models.return_request import ReturnRequest
from app.api.auth import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ============================================================
# GET USER ORDERS
# ============================================================

@router.get("/")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    orders = (
        db.query(Order)
        .filter(
            Order.user_id == current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

    result = []

    for order in orders:

        # Find return request for this order
        return_request = (
            db.query(ReturnRequest)
            .filter(
                ReturnRequest.order_id == order.id,
                ReturnRequest.user_id == current_user.id
            )
            .order_by(
                ReturnRequest.created_at.desc()
            )
            .first()
        )

        order_data = {
            "id": order.id,
            "total": order.total,
            "order_status": order.order_status,
            "payment_status": order.payment_status,
            "created_at": order.created_at,

            # Important for return window
            "delivered_at": getattr(
                order,
                "delivered_at",
                None
            ),

            "return_request": None
        }

        # Return request information
        if return_request:

            order_data["return_request"] = {
                "id": return_request.id,
                "reason": return_request.reason,
                "comment": getattr(
                    return_request,
                    "comment",
                    None
                ),
                "status": return_request.status,
                "created_at": return_request.created_at
            }

        result.append(order_data)

    return result

