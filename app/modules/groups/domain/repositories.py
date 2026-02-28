"""Abstract repository interface for the groups domain."""
from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.groups.domain.entities import Group


class AbstractGroupRepository(ABC):
    """Port (interface) for group persistence operations."""

    @abstractmethod
    async def create(self, group: Group) -> Group:
        """Persist a new group and return the saved entity."""
        ...

    @abstractmethod
    async def get_by_id(self, group_id: UUID) -> Group | None:
        """Return a group by primary key, or None if not found."""
        ...

    @abstractmethod
    async def get_all_by_host(self, host_id: UUID) -> list[Group]:
        """Return all groups where the given user is the host."""
        ...

    @abstractmethod
    async def get_all_active(self) -> list[Group]:
        """Return all groups that are currently active."""
        ...

    @abstractmethod
    async def update(self, group: Group) -> Group:
        """Persist changes to an existing group."""
        ...

    @abstractmethod
    async def delete(self, group_id: UUID) -> None:
        """Hard-delete a group by primary key."""
        ...


__all__ = ["AbstractGroupRepository"]
