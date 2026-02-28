"""Abstract repository interface for the members domain."""
from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.members.domain.entities import Member


class AbstractMemberRepository(ABC):
    """Port (interface) for member persistence operations."""

    @abstractmethod
    async def create(self, member: Member) -> Member:
        ...

    @abstractmethod
    async def get_by_id(self, member_id: UUID) -> Member | None:
        ...

    @abstractmethod
    async def get_by_group(self, group_id: UUID) -> list[Member]:
        """Return all members (any status) for a given group."""
        ...

    @abstractmethod
    async def get_by_user_and_group(
        self, user_id: UUID, group_id: UUID
    ) -> Member | None:
        ...

    @abstractmethod
    async def count_active(self, group_id: UUID) -> int:
        """Count confirmed (ACTIVE) members in a group."""
        ...

    @abstractmethod
    async def update(self, member: Member) -> Member:
        ...

    @abstractmethod
    async def delete(self, member_id: UUID) -> None:
        ...


__all__ = ["AbstractMemberRepository"]
