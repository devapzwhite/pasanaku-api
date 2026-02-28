"""Pydantic v2 schemas for auth request/response DTOs."""
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.modules.auth.domain.entities import UserRole


# ---------------------------------------------------------------------------
# Request schemas (input)
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Payload for CU-01 - registrar nuevo usuario."""

    full_name: str = Field(..., min_length=2, max_length=100, examples=["Juan Perez"])
    email: EmailStr = Field(..., examples=["juan@example.com"])
    phone: str = Field(..., min_length=7, max_length=20, examples=["+591 70000000"])
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = Field(default=UserRole.PLAYER)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Las contrasenas no coinciden")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 7:
            raise ValueError("Ingrese un numero de telefono valido")
        return v


class LoginRequest(BaseModel):
    """Payload for CU-02 - iniciar sesion."""

    email: EmailStr = Field(..., examples=["juan@example.com"])
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Payload for refreshing the access token."""

    refresh_token: str


# ---------------------------------------------------------------------------
# Response schemas (output)
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Public user representation - never exposes hashed_password."""

    id: UUID
    full_name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT tokens returned after successful login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Response after successful registration."""

    message: str = "Usuario registrado exitosamente"
    user: UserResponse


__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "UserResponse",
    "TokenResponse",
    "RegisterResponse",
]
