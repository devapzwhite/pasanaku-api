"""Security utilities: password hashing and JWT token management."""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordManager:
    """Handles password hashing and verification."""

    @staticmethod
    def hash(plain_password: str) -> str:
        """Hash a plain password using bcrypt."""
        return pwd_context.hash(plain_password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)


class TokenManager:
    """Handles JWT access and refresh token creation and decoding."""

    @staticmethod
    def create_access_token(
        subject: str | Any,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a short-lived JWT access token."""
        expire = datetime.now(timezone.utc) + (
            expires_delta
            if expires_delta
            else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(
        subject: str | Any,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a long-lived JWT refresh token."""
        expire = datetime.now(timezone.utc) + (
            expires_delta
            if expires_delta
            else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        payload = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate a JWT token. Raises JWTError on failure."""
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )


# Module-level singletons for convenience
password_manager = PasswordManager()
token_manager = TokenManager()

__all__ = [
    "password_manager",
    "token_manager",
    "JWTError",
]
