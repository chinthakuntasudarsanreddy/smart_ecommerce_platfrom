from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/by-email")
def get_user_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "email": user.email
    }