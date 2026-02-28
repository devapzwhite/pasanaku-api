"""Auth use cases (application service layer).

Each use case is a single-responsibility class that orchestrates domain
logic and infrastructure via dependency injection. Follows SRP + DIP.
"""
from dataclasses import dataclass

from app.core.security import password_manager, token_manager
from app.modules.auth.application.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.domain.entities import User, UserRole
from app.modules.auth.domain.repositories import AbstractUserRepository
from app.shared.exceptions import (
    DuplicateEntityError,
    InactiveUserError,
    InvalidCredentialsError,
)
from jose import JWTError
from fastapi import HTTPException, status


@dataclass
class RegisterUseCase:
    """CU-01 - Registrar como anfitrin o jugador.

    Validates uniqueness, hashes password, persists the new user.
    """

    user_repo: AbstractUserRepository

    async def execute(self, payload: RegisterRequest) -> RegisterResponse:
        # 1. Check email uniqueness
        if await self.user_repo.email_exists(payload.email):
            raise DuplicateEntityError(
                "Este email ya esta registrado. Por favor inicie sesion"
            )

        # 2. Build domain entity
        user = User(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=password_manager.hash(payload.password),
            role=UserRole(payload.role),
        )

        # 3. Persist
        saved_user = await self.user_repo.create(user)

        return RegisterResponse(
            user=UserResponse(
                id=saved_user.id,
                full_name=saved_user.full_name,
                email=saved_user.email,
                phone=saved_user.phone,
                role=saved_user.role,
                is_active=saved_user.is_active,
            )
        )


@dataclass
class LoginUseCase:
    """CU-02 - Iniciar sesion y obtener JWT tokens."""

    user_repo: AbstractUserRepository

    async def execute(self, payload: LoginRequest) -> TokenResponse:
        # 1. Find user
        user = await self.user_repo.get_by_email(payload.email)
        if user is None:
            raise InvalidCredentialsError(
                "Usuario no encontrado. Por favor registrese"
            )

        # 2. Verify password
        if not password_manager.verify(payload.password, user.hashed_password):
            raise InvalidCredentialsError("Email o contrasena incorrectos")

        # 3. Check active status
        if not user.is_active:
            raise InactiveUserError(
                "Su cuenta ha sido desactivada. Contacte al administrador"
            )

        # 4. Generate tokens
        access_token = token_manager.create_access_token(subject=str(user.id))
        refresh_token = token_manager.create_refresh_token(subject=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


@dataclass
class RefreshTokenUseCase:
    """Refresh the access token using a valid refresh token."""

    user_repo: AbstractUserRepository

    async def execute(self, payload: RefreshTokenRequest) -> TokenResponse:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token_data = token_manager.decode_token(payload.refresh_token)
            if token_data.get("type") != "refresh":
                raise credentials_exception
            user_id: str = token_data.get("sub", "")
        except JWTError:
            raise credentials_exception

        from uuid import UUID
        user = await self.user_repo.get_by_id(UUID(user_id))
        if user is None or not user.is_active:
            raise credentials_exception

        return TokenResponse(
            access_token=token_manager.create_access_token(subject=user_id),
            refresh_token=token_manager.create_refresh_token(subject=user_id),
        )


__all__ = ["RegisterUseCase", "LoginUseCase", "RefreshTokenUseCase"]
