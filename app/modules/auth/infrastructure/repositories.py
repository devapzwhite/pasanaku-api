"""Concrete SQLAlchemy implementation of AbstractUserRepository.

This is the infrastructure adapter that satisfies the domain port.
All DB queries use async SQLAlchemy 2.x select() syntax.
"""
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.entities import User, UserRole
from app.modules.auth.domain.repositories import AbstractUserRepository
from app.modules.auth.infrastructure.models import UserModel


class SQLAlchemyUserRepository(AbstractUserRepository):
    """Adapter: translates domain User <-> SQLAlchemy UserModel."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        """Convert ORM model -> domain entity."""
        return User(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            phone=model.phone,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        """Convert domain entity -> ORM model."""
        return UserModel(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    # ------------------------------------------------------------------
    # AbstractUserRepository implementation
    # ------------------------------------------------------------------

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()  # get DB-generated values without committing
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.phone == phone)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one()
        model.full_name = user.full_name
        model.email = user.email
        model.phone = user.phone
        model.hashed_password = user.hashed_password
        model.role = user.role
        model.is_active = user.is_active
        model.updated_at = user.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one()
        await self._session.delete(model)

    async def email_exists(self, email: str) -> bool:
        result = await self._session.execute(
            select(exists().where(UserModel.email == email))
        )
        return result.scalar()


__all__ = ["SQLAlchemyUserRepository"]
