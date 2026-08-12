from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.deps import require_roles

from app.models.user import User
from app.models.user import UserRole


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


@router.get("/admin-only")
def admin_only(
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return {
        "message": "Admin access granted",
        "user": current_user.email
    }


@router.get("/staff-or-admin")
def staff_or_admin(
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.STAFF
        )
    )
):
    return {
        "message": "Staff/Admin access granted",
        "user": current_user.email
    }