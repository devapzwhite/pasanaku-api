"""FastAPI dependency injection for authentication and database."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import token_manager
from app.shared.database import get_db

# Bearer token scheme (no auto_error so we can provide custom messages)
oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(oauth2_scheme),
    ],
) -> str:
    """Extract and validate the user ID from the JWT access token.

    Raises HTTP 401 if token is missing, invalid, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise credentials_exception

    try:
        payload = token_manager.decode_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return user_id


# Type alias for DI shorthand
CurrentUserID = Annotated[str, Depends(get_current_user_id)]
DBSession = Annotated[AsyncSession, Depends(get_db)]

__all__ = ["CurrentUserID", "DBSession", "get_current_user_id", "get_db"]
