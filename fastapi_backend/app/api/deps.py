import jwt

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token

from app.models.user import User
from app.models.user import UserRole


security = HTTPBearer()


def get_current_user(

    credentials: HTTPAuthorizationCredentials =
        Depends(security),

    db: Session = Depends(get_db)

):

    token = credentials.credentials

    try:

        payload = decode_token(token)

        if payload.get("type") != "access":

            raise HTTPException(
                status_code=401,
                detail="Access token required"
            )

        user_id = int(
            payload["sub"]
        )

    except (
        jwt.InvalidTokenError,
        KeyError,
        ValueError
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.get(
        User,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


def require_roles(*allowed_roles: UserRole):

    def role_checker(

        current_user: User =
            Depends(get_current_user)

    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker