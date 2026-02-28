"""SQLAlchemy implementation of the AbstractGroupRepository."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.groups.domain.entities import Frequency, Group, GroupStatus
from app.modules.groups.domain.repositories import AbstractGroupRepository
from app.modules.groups.infrastructure.models import GroupModel


class SQLAlchemyGroupRepository(AbstractGroupRepository):
    """Concrete repository backed by PostgreSQL via SQLAlchemy async."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_domain(model: GroupModel) -> Group:
        return Group(
            id=model.id,
            name=model.name,
            description=model.description,
            host_id=model.host_id,
            amount_per_member=model.amount_per_member,
            frequency=Frequency(model.frequency),
            max_members=model.max_members,
            status=GroupStatus(model.status),
            start_date=model.start_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(group: Group) -> GroupModel:
        model = GroupModel()
        model.id = group.id
        model.name = group.name
        model.description = group.description
        model.host_id = group.host_id
        model.amount_per_member = group.amount_per_member
        model.frequency = group.frequency
        model.max_members = group.max_members
        model.status = group.status
        model.start_date = group.start_date
        model.created_at = group.created_at
        model.updated_at = group.updated_at
        return model

    # ------------------------------------------------------------------
    # AbstractGroupRepository implementation
    # ------------------------------------------------------------------

    async def create(self, group: Group) -> Group:
        model = self._to_model(group)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, group_id: UUID) -> Group | None:
        result = await self._session.execute(
            select(GroupModel).where(GroupModel.id == group_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_all_by_host(self, host_id: UUID) -> list[Group]:
        result = await self._session.execute(
            select(GroupModel).where(GroupModel.host_id == host_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_all_active(self) -> list[Group]:
        result = await self._session.execute(
            select(GroupModel).where(GroupModel.status == GroupStatus.ACTIVE)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, group: Group) -> Group:
        result = await self._session.execute(
            select(GroupModel).where(GroupModel.id == group.id)
        )
        model = result.scalar_one()
        model.name = group.name
        model.description = group.description
        model.amount_per_member = group.amount_per_member
        model.frequency = group.frequency
        model.max_members = group.max_members
        model.status = group.status
        model.updated_at = group.updated_at
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, group_id: UUID) -> None:
        result = await self._session.execute(
            select(GroupModel).where(GroupModel.id == group_id)
        )
        model = result.scalar_one()
        await self._session.delete(model)
        await self._session.commit()


__all__ = ["SQLAlchemyGroupRepository"]
