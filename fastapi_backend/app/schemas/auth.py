from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

from app.models.user import UserRole


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=120
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class RefreshRequest(BaseModel):

    refresh_token: str


class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    role: UserRole

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"

    expires_in: int

    user: UserResponse