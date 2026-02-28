"""Abstract repository interface for the auth domain.

Following the Dependency Inversion Principle, the domain defines the
contract. The infrastructure layer provides the concrete implementation.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.auth.domain.entities import User


class AbstractUserRepository(ABC):
    """Port (interface) for user persistence operations."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user and return the saved entity."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by primary key, or None if not found."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Return a user by email address, or None if not found."""
        ...

    @abstractmethod
    async def get_by_phone(self, phone: str) -> User | None:
        """Return a user by phone number, or None if not found."""
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Persist changes to an existing user and return the updated entity."""
        ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Hard-delete a user by primary key."""
        ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Return True if an account with this email already exists."""
        ...


__all__ = ["AbstractUserRepository"]
