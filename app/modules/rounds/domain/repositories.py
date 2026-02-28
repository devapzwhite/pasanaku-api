"""Abstract repository interface for the rounds domain."""
from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.rounds.domain.entities import Round


class AbstractRoundRepository(ABC):
    @abstractmethod
    async def create(self, round_: Round) -> Round: ...

    @abstractmethod
    async def get_by_id(self, round_id: UUID) -> Round | None: ...

    @abstractmethod
    async def get_by_group(self, group_id: UUID) -> list[Round]: ...

    @abstractmethod
    async def update(self, round_: Round) -> Round: ...

    @abstractmethod
    async def delete(self, round_id: UUID) -> None: ...


__all__ = ["AbstractRoundRepository"]
