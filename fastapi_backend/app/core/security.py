from datetime import datetime
from datetime import timedelta
from datetime import timezone

import jwt

from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_token(
    user_id: int,
    token_type: str,
    expires_delta: timedelta
):

    now = datetime.now(timezone.utc)

    payload = {

        "sub": str(user_id),

        "type": token_type,

        "iat": now,

        "exp": now + expires_delta

    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def create_access_token(user_id: int):

    return create_token(

        user_id,

        "access",

        timedelta(
            minutes=settings.access_token_expire_minutes
        )

    )


def create_refresh_token(user_id: int):

    return create_token(

        user_id,

        "refresh",

        timedelta(
            days=settings.refresh_token_expire_days
        )

    )


def decode_token(token: str):

    return jwt.decode(

        token,

        settings.jwt_secret_key,

        algorithms=[settings.jwt_algorithm]

    )