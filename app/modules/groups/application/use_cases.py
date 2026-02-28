"""Groups use cases (application service layer).

CU-02: Crear grupo Pasanaku (solo anfitrion)
CU-03: Listar grupos disponibles
CU-04: Obtener detalle de un grupo
"""
from dataclasses import dataclass
from uuid import UUID

from app.modules.groups.application.schemas import (
    CreateGroupRequest,
    GroupResponse,
    UpdateGroupRequest,
)
from app.modules.groups.domain.entities import Group
from app.modules.groups.domain.repositories import AbstractGroupRepository
from app.shared.exceptions import NotFoundError, ForbiddenError


@dataclass
class CreateGroupUseCase:
    """CU-02 - Crear un nuevo grupo Pasanaku.

    Only authenticated users with role HOST may create groups.
    """

    group_repo: AbstractGroupRepository

    async def execute(
        self, payload: CreateGroupRequest, host_id: UUID
    ) -> GroupResponse:
        group = Group(
            name=payload.name,
            description=payload.description,
            host_id=host_id,
            amount_per_member=payload.amount_per_member,
            frequency=payload.frequency,
            max_members=payload.max_members,
            start_date=payload.start_date,
        )
        saved = await self.group_repo.create(group)
        return GroupResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            host_id=saved.host_id,
            amount_per_member=saved.amount_per_member,
            frequency=saved.frequency,
            max_members=saved.max_members,
            status=saved.status,
            start_date=saved.start_date,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )


@dataclass
class ListActiveGroupsUseCase:
    """CU-03 - Listar todos los grupos activos disponibles."""

    group_repo: AbstractGroupRepository

    async def execute(self) -> list[GroupResponse]:
        groups = await self.group_repo.get_all_active()
        return [
            GroupResponse(
                id=g.id,
                name=g.name,
                description=g.description,
                host_id=g.host_id,
                amount_per_member=g.amount_per_member,
                frequency=g.frequency,
                max_members=g.max_members,
                status=g.status,
                start_date=g.start_date,
                created_at=g.created_at,
                updated_at=g.updated_at,
            )
            for g in groups
        ]


@dataclass
class GetGroupUseCase:
    """CU-04 - Obtener detalle de un grupo por ID."""

    group_repo: AbstractGroupRepository

    async def execute(self, group_id: UUID) -> GroupResponse:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        return GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            host_id=group.host_id,
            amount_per_member=group.amount_per_member,
            frequency=group.frequency,
            max_members=group.max_members,
            status=group.status,
            start_date=group.start_date,
            created_at=group.created_at,
            updated_at=group.updated_at,
        )


@dataclass
class UpdateGroupUseCase:
    """Update mutable fields of a group (host only)."""

    group_repo: AbstractGroupRepository

    async def execute(
        self, group_id: UUID, payload: UpdateGroupRequest, requester_id: UUID
    ) -> GroupResponse:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        if group.host_id != requester_id:
            raise ForbiddenError("Solo el anfitrion puede modificar el grupo")

        if payload.name is not None:
            group.name = payload.name
        if payload.description is not None:
            group.description = payload.description
        if payload.amount_per_member is not None:
            group.amount_per_member = payload.amount_per_member
        if payload.frequency is not None:
            group.frequency = payload.frequency
        if payload.max_members is not None:
            group.max_members = payload.max_members

        saved = await self.group_repo.update(group)
        return GroupResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            host_id=saved.host_id,
            amount_per_member=saved.amount_per_member,
            frequency=saved.frequency,
            max_members=saved.max_members,
            status=saved.status,
            start_date=saved.start_date,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )


@dataclass
class DeleteGroupUseCase:
    """Soft-cancel or hard-delete a group (host only)."""

    group_repo: AbstractGroupRepository

    async def execute(self, group_id: UUID, requester_id: UUID) -> None:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        if group.host_id != requester_id:
            raise ForbiddenError("Solo el anfitrion puede eliminar el grupo")
        await self.group_repo.delete(group_id)


__all__ = [
    "CreateGroupUseCase",
    "ListActiveGroupsUseCase",
    "GetGroupUseCase",
    "UpdateGroupUseCase",
    "DeleteGroupUseCase",
]
