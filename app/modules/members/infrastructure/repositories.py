"""SQLAlchemy implementation of the AbstractMemberRepository."""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.members.domain.entities import Member, MemberStatus
from app.modules.members.domain.repositories import AbstractMemberRepository
from app.modules.members.infrastructure.models import MemberModel


class SQLAlchemyMemberRepository(AbstractMemberRepository):
    """Concrete repository backed by PostgreSQL via SQLAlchemy async."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: MemberModel) -> Member:
        return Member(
            id=model.id,
            group_id=model.group_id,
            user_id=model.user_id,
            turn_number=model.turn_number,
            status=MemberStatus(model.status),
            joined_at=model.joined_at,
            updated_at=model.updated_at,
        )

    async def create(self, member: Member) -> Member:
        model = MemberModel()
        model.id = member.id
        model.group_id = member.group_id
        model.user_id = member.user_id
        model.turn_number = member.turn_number
        model.status = member.status
        model.joined_at = member.joined_at
        model.updated_at = member.updated_at
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, member_id: UUID) -> Member | None:
        result = await self._session.execute(
            select(MemberModel).where(MemberModel.id == member_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_group(self, group_id: UUID) -> list[Member]:
        result = await self._session.execute(
            select(MemberModel).where(MemberModel.group_id == group_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_user_and_group(
        self, user_id: UUID, group_id: UUID
    ) -> Member | None:
        result = await self._session.execute(
            select(MemberModel).where(
                MemberModel.user_id == user_id,
                MemberModel.group_id == group_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def count_active(self, group_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).where(
                MemberModel.group_id == group_id,
                MemberModel.status == MemberStatus.ACTIVE,
            )
        )
        return result.scalar_one()

    async def update(self, member: Member) -> Member:
        result = await self._session.execute(
            select(MemberModel).where(MemberModel.id == member.id)
        )
        model = result.scalar_one()
        model.turn_number = member.turn_number
        model.status = member.status
        model.updated_at = member.updated_at
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, member_id: UUID) -> None:
        result = await self._session.execute(
            select(MemberModel).where(MemberModel.id == member_id)
        )
        model = result.scalar_one()
        await self._session.delete(model)
        await self._session.commit()


__all__ = ["SQLAlchemyMemberRepository"]
