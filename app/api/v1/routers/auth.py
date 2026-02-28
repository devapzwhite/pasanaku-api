"""Auth API router - HTTP layer for authentication endpoints.

Maps HTTP requests -> use cases -> HTTP responses.
All exception translation from domain errors to HTTP happens here.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUserID, DBSession
from app.modules.auth.application.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.application.use_cases import (
    LoginUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
)
from app.modules.auth.infrastructure.repositories import SQLAlchemyUserRepository
from app.shared.exceptions import (
    DuplicateEntityError,
    InactiveUserError,
    InvalidCredentialsError,
)

router = APIRouter()


def _get_user_repo(db: DBSession) -> SQLAlchemyUserRepository:
    """Factory function: build repository from injected session."""
    return SQLAlchemyUserRepository(session=db)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CU-01 Registrarse como anfitrin o jugador",
)
async def register(
    payload: RegisterRequest,
    db: DBSession,
) -> RegisterResponse:
    """Register a new user (host or player)."""
    use_case = RegisterUseCase(user_repo=_get_user_repo(db))
    try:
        return await use_case.execute(payload)
    except DuplicateEntityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="CU-02 Iniciar sesin",
)
async def login(
    payload: LoginRequest,
    db: DBSession,
) -> TokenResponse:
    """Authenticate a user and return JWT access + refresh tokens."""
    use_case = LoginUseCase(user_repo=_get_user_repo(db))
    try:
        return await use_case.execute(payload)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exc.message,
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar access token usando refresh token",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: DBSession,
) -> TokenResponse:
    """Issue a new access token given a valid refresh token."""
    use_case = RefreshTokenUseCase(user_repo=_get_user_repo(db))
    return await use_case.execute(payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario autenticado",
)
async def get_me(
    current_user_id: CurrentUserID,
    db: DBSession,
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    from uuid import UUID

    repo = _get_user_repo(db)
    user = await repo.get_by_id(UUID(current_user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="CU-03 Cerrar sesin (cliente elimina token)",
)
async def logout(current_user_id: CurrentUserID) -> None:
    """Logout endpoint - token invalidation is handled client-side.

    The client should delete the stored JWT tokens.
    For server-side blacklisting, add token to a Redis blocklist here.
    """
    return None


__all__ = ["router"]
