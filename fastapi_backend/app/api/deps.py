import json
import secrets
import ssl
import urllib.request
from functools import lru_cache

import certifi
import jwt

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


# ============================================================
# AUTHENTICATION
# ============================================================

bearer_scheme = HTTPBearer(auto_error=True)

AUTH0_DOMAIN = settings.auth0_domain.strip().rstrip("/")
AUTH0_AUDIENCE = settings.auth0_audience.strip()
AUTH0_ISSUER = settings.auth0_issuer.strip().rstrip("/") + "/"

# Auth0 endpoints
JWKS_URL = f"{AUTH0_ISSUER}.well-known/jwks.json"

# IMPORTANT:
# AUTH0_DOMAIN does not contain https://,
# so we add it here.
USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"


print("==============================================")
print("AUTH0 CONFIGURATION")
print("DOMAIN   :", AUTH0_DOMAIN)
print("AUDIENCE :", AUTH0_AUDIENCE)
print("ISSUER   :", AUTH0_ISSUER)
print("JWKS URL :", JWKS_URL)
print("USERINFO :", USERINFO_URL)
print("==============================================")


# ============================================================
# AUTH0 JWKS CLIENT
# ============================================================

@lru_cache()
def get_jwks_client():

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    return jwt.PyJWKClient(
        JWKS_URL,
        ssl_context=ssl_context,
    )


# ============================================================
# GET AUTH0 USER INFO
# ============================================================

def get_auth0_userinfo(token: str):

    try:

        ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )

        request = urllib.request.Request(
            USERINFO_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="GET",
        )

        with urllib.request.urlopen(
            request,
            context=ssl_context,
            timeout=10,
        ) as response:

            data = response.read().decode("utf-8")

            userinfo = json.loads(data)

            print("AUTH0 USERINFO SUCCESS")

            return userinfo

    except Exception as exc:

        print(
            "AUTH0 USERINFO ERROR:",
            type(exc).__name__,
            str(exc),
        )

        return {}


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
):

    token = credentials.credentials

    # ========================================================
    # VALIDATE AUTH0 JWT
    # ========================================================

    try:

        signing_key = (
            get_jwks_client()
            .get_signing_key_from_jwt(token)
        )

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
            detail="Auth0 token has expired",
        )

    except jwt.InvalidAudienceError:

        print("AUTH0 ERROR: Invalid audience")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 audience",
        )

    except jwt.InvalidIssuerError:

        print("AUTH0 ERROR: Invalid issuer")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 issuer",
        )

    except jwt.PyJWKClientError as exc:

        print("AUTH0 ERROR: JWKS error:", exc)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to retrieve Auth0 signing key",
        )

    except jwt.InvalidTokenError as exc:

        print("AUTH0 ERROR: Invalid token:", exc)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 token",
        )

    except Exception as exc:

        print(
            "AUTH0 ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to authenticate with Auth0",
        )

    # ========================================================
    # GET AUTH0 SUBJECT
    # ========================================================

    auth0_sub = payload.get("sub")

    if not auth0_sub:

        print("AUTH0 ERROR: Missing sub")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth0 token does not contain sub",
        )

    print("AUTH0 SUB:", auth0_sub)

    # ========================================================
    # FIND USER BY AUTH0 SUB
    # ========================================================

    user = (
        db.query(User)
        .filter(User.auth0_sub == auth0_sub)
        .first()
    )

    if user:

        print(
            "DATABASE USER FOUND:",
            user.id,
            user.email,
        )

        return user

    print("USER NOT FOUND BY AUTH0 SUB")

    # ========================================================
    # GET EMAIL FROM JWT
    # ========================================================

    email = payload.get("email")

    name = (
        payload.get("name")
        or payload.get("nickname")
        or "Auth0 User"
    )

    # ========================================================
    # EMAIL NOT IN JWT
    # USE AUTH0 /userinfo
    # ========================================================

    if not email:

        print(
            "EMAIL NOT FOUND IN TOKEN. "
            "Calling Auth0 /userinfo..."
        )

        userinfo = get_auth0_userinfo(token)

        email = userinfo.get("email")

        name = (
            userinfo.get("name")
            or userinfo.get("nickname")
            or name
        )

        print("USERINFO EMAIL:", email)
        print("USERINFO NAME:", name)

    # ========================================================
    # EMAIL STILL NOT AVAILABLE
    # ========================================================

    if not email:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Unable to get email from Auth0. "
                "Please make sure the email scope is enabled."
            ),
        )

    # ========================================================
    # FIND USER BY EMAIL
    # ========================================================

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user:

        print(
            "DATABASE USER FOUND BY EMAIL:",
            user.id,
            user.email,
        )

        user.auth0_sub = auth0_sub

        db.commit()
        db.refresh(user)

        print("AUTH0 SUB UPDATED")

        return user

    # ========================================================
    # CREATE NEW USER
    # ========================================================

    print("CREATING NEW DATABASE USER")

    user = User(
        name=name,
        email=email,
        password=None,
        auth0_sub=auth0_sub,
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    print(
        "NEW DATABASE USER CREATED:",
        user.id,
        user.email,
    )

    return user


# ============================================================
# ROLE AUTHORIZATION
# ============================================================

def require_roles(*allowed_roles):

    def role_checker(
        current_user: User = Depends(get_current_user),
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
                ),
            )

        return current_user

    return role_checker


# ============================================================
# INTERNAL ADMIN API KEY
# ============================================================

def require_internal_admin_api_key(
    x_internal_admin_key: str = Header(...),
):

    expected_key = settings.internal_admin_api_key.strip()

    if not expected_key:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal admin API key is not configured",
        )

    if not secrets.compare_digest(
        x_internal_admin_key,
        expected_key,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal admin API key",
        )

    return True