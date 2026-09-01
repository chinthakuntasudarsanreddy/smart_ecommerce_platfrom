from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user

from app.models.user import User
from app.models.order import Order


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.get("/")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return orders