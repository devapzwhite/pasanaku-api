"""Abstract repository interface for the payments domain."""
from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.payments.domain.entities import Payment


class AbstractPaymentRepository(ABC):
    @abstractmethod
    async def create(self, payment: Payment) -> Payment: ...

    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> Payment | None: ...

    @abstractmethod
    async def get_by_round(self, round_id: UUID) -> list[Payment]: ...

    @abstractmethod
    async def get_by_payer_and_round(
        self, payer_id: UUID, round_id: UUID
    ) -> Payment | None: ...

    @abstractmethod
    async def update(self, payment: Payment) -> Payment: ...


__all__ = ["AbstractPaymentRepository"]
