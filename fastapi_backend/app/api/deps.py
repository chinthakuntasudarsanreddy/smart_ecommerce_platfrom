
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


# ============================================================
# AUTH0 BEARER SECURITY
# ============================================================

bearer_scheme = HTTPBearer(auto_error=True)


# ============================================================
# AUTH0 CONFIG
# ============================================================

AUTH0_DOMAIN = settings.auth0_domain.strip().rstrip("/")
AUTH0_AUDIENCE = settings.auth0_audience.strip()
AUTH0_ISSUER = settings.auth0_issuer.strip().rstrip("/") + "/"

# Example:
# https://dev-xxxxx.us.auth0.com/
JWKS_URL = f"{AUTH0_ISSUER}.well-known/jwks.json"


print("==============================================")
print("AUTH0 CONFIGURATION")
print("DOMAIN   :", AUTH0_DOMAIN)
print("AUDIENCE :", AUTH0_AUDIENCE)
print("ISSUER   :", AUTH0_ISSUER)
print("JWKS URL :", JWKS_URL)
print("==============================================")


# ============================================================
# JWKS CLIENT
# ============================================================

@lru_cache()
def get_jwks_client():
    return jwt.PyJWKClient(JWKS_URL)


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        # ----------------------------------------------------
        # Get signing key from Auth0 JWKS
        # ----------------------------------------------------

        signing_key = get_jwks_client().get_signing_key_from_jwt(
            token
        )

        # ----------------------------------------------------
        # Decode and validate Auth0 token
        # ----------------------------------------------------

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )

        print("Auth0 token validated successfully")
        print("Auth0 payload:", payload)

    except jwt.ExpiredSignatureError:
        print("AUTH0 ERROR: Token expired")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth0 token has expired"
        )

    except jwt.InvalidAudienceError:
        print("AUTH0 ERROR: Invalid audience")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 audience"
        )

    except jwt.InvalidIssuerError:
        print("AUTH0 ERROR: Invalid issuer")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 issuer"
        )

    except jwt.PyJWKClientError as exc:
        print("AUTH0 ERROR: JWKS error:", exc)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to retrieve Auth0 signing key"
        )

    except jwt.InvalidTokenError as exc:
        print("AUTH0 ERROR: Invalid token:", exc)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 token"
        )

    except Exception as exc:
        print("AUTH0 ERROR:", type(exc).__name__, str(exc))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to authenticate with Auth0"
        )

    # ========================================================
    # GET AUTH0 USER ID
    # ========================================================

    auth0_sub = payload.get("sub")

    if not auth0_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth0 token does not contain sub"
        )

    # ========================================================
    # FIND LOCAL USER BY AUTH0 SUB
    # ========================================================

    user = (
        db.query(User)
        .filter(User.auth0_sub == auth0_sub)
        .first()
    )

    if user:
        return user

    # ========================================================
    # GET USER INFORMATION
    # ========================================================

    email = payload.get("email")
    name = (
        payload.get("name")
        or payload.get("nickname")
        or email
        or "Auth0 User"
    )

    # ========================================================
    # EMAIL MAY NOT BE PRESENT IN ACCESS TOKEN
    # ========================================================

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Auth0 token does not contain email. "
                "Configure email access or use the /userinfo endpoint."
            )
        )

    # ========================================================
    # CHECK EXISTING LOCAL USER BY EMAIL
    # ========================================================

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user:
        user.auth0_sub = auth0_sub

        db.commit()
        db.refresh(user)

        return user

    # ========================================================
    # CREATE NEW LOCAL USER
    # ========================================================

    user = User(
        name=name,
        email=email,
        password=None,
        auth0_sub=auth0_sub,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# ROLE CHECK
# ============================================================

def require_roles(*allowed_roles):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        current_role = (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else current_user.role
        )

        normalized_roles = [
            role.value
            if hasattr(role, "value")
            else role
            for role in allowed_roles
        ]

        if current_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this resource"
                )
            )

        return current_user

    return role_checker
