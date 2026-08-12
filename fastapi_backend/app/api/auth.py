import jwt

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

from app.core.security import hash_password
from app.core.security import verify_password
from app.core.security import create_access_token
from app.core.security import create_refresh_token
from app.core.security import decode_token

from app.models.user import User
from app.models.user import UserRole

from app.schemas.auth import RegisterRequest
from app.schemas.auth import LoginRequest
from app.schemas.auth import RefreshRequest
from app.schemas.auth import TokenResponse
from app.schemas.auth import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def create_token_response(user: User):

    return TokenResponse(

        access_token=create_access_token(
            user.id
        ),

        refresh_token=create_refresh_token(
            user.id
        ),

        expires_in=(
            settings.access_token_expire_minutes
            * 60
        ),

        user=UserResponse.model_validate(user)

    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    email = data.email.lower()

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user = User(

        name=data.name,

        email=email,

        password=hash_password(
            data.password
        ),

        role=UserRole.CUSTOMER

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return create_token_response(user)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    email = data.email.lower()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if (
        not user
        or not user.password
        or not verify_password(
            data.password,
            user.password
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return create_token_response(user)


@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):

    try:

        payload = decode_token(
            data.refresh_token
        )

        if payload.get("type") != "refresh":

            raise HTTPException(
                status_code=401,
                detail="Refresh token required"
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
            detail="Invalid or expired refresh token"
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

    return create_token_response(user)
from app.api.deps import get_current_user


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User =
        Depends(get_current_user)
):

    return current_user