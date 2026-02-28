"""SQLAlchemy implementation of the AbstractPaymentRepository."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.domain.entities import Payment, PaymentStatus
from app.modules.payments.domain.repositories import AbstractPaymentRepository
from app.modules.payments.infrastructure.models import PaymentModel


class SQLAlchemyPaymentRepository(AbstractPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            round_id=model.round_id,
            payer_id=model.payer_id,
            amount=model.amount,
            status=PaymentStatus(model.status),
            paid_at=model.paid_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, payment: Payment) -> Payment:
        model = PaymentModel()
        model.id = payment.id
        model.round_id = payment.round_id
        model.payer_id = payment.payer_id
        model.amount = payment.amount
        model.status = payment.status
        model.paid_at = payment.paid_at
        model.created_at = payment.created_at
        model.updated_at = payment.updated_at
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_round(self, round_id: UUID) -> list[Payment]:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.round_id == round_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_payer_and_round(
        self, payer_id: UUID, round_id: UUID
    ) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(
                PaymentModel.payer_id == payer_id,
                PaymentModel.round_id == round_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, payment: Payment) -> Payment:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == payment.id)
        )
        model = result.scalar_one()
        model.status = payment.status
        model.paid_at = payment.paid_at
        model.updated_at = payment.updated_at
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)


__all__ = ["SQLAlchemyPaymentRepository"]
