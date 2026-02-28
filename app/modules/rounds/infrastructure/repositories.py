"""SQLAlchemy implementation of the AbstractRoundRepository."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rounds.domain.entities import Round, RoundStatus
from app.modules.rounds.domain.repositories import AbstractRoundRepository
from app.modules.rounds.infrastructure.models import RoundModel


class SQLAlchemyRoundRepository(AbstractRoundRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: RoundModel) -> Round:
        return Round(
            id=model.id,
            group_id=model.group_id,
            beneficiary_id=model.beneficiary_id,
            turn_number=model.turn_number,
            due_date=model.due_date,
            total_amount=model.total_amount,
            status=RoundStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, round_: Round) -> Round:
        model = RoundModel()
        model.id = round_.id
        model.group_id = round_.group_id
        model.beneficiary_id = round_.beneficiary_id
        model.turn_number = round_.turn_number
        model.due_date = round_.due_date
        model.total_amount = round_.total_amount
        model.status = round_.status
        model.created_at = round_.created_at
        model.updated_at = round_.updated_at
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, round_id: UUID) -> Round | None:
        result = await self._session.execute(
            select(RoundModel).where(RoundModel.id == round_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_group(self, group_id: UUID) -> list[Round]:
        result = await self._session.execute(
            select(RoundModel)
            .where(RoundModel.group_id == group_id)
            .order_by(RoundModel.turn_number)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, round_: Round) -> Round:
        result = await self._session.execute(
            select(RoundModel).where(RoundModel.id == round_.id)
        )
        model = result.scalar_one()
        model.status = round_.status
        model.updated_at = round_.updated_at
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, round_id: UUID) -> None:
        result = await self._session.execute(
            select(RoundModel).where(RoundModel.id == round_id)
        )
        model = result.scalar_one()
        await self._session.delete(model)
        await self._session.commit()


__all__ = ["SQLAlchemyRoundRepository"]
