"""Members use cases.

CU-05: Agregar miembro a un grupo
CU-06: Listar miembros de un grupo
"""
from dataclasses import dataclass
from uuid import UUID

from app.modules.members.application.schemas import AddMemberRequest, MemberResponse
from app.modules.members.domain.entities import Member
from app.modules.members.domain.repositories import AbstractMemberRepository
from app.modules.groups.domain.repositories import AbstractGroupRepository
from app.shared.exceptions import NotFoundError, ForbiddenError, DuplicateEntityError


def _to_response(m: Member) -> MemberResponse:
    return MemberResponse(
        id=m.id,
        group_id=m.group_id,
        user_id=m.user_id,
        turn_number=m.turn_number,
        status=m.status,
        joined_at=m.joined_at,
        updated_at=m.updated_at,
    )


@dataclass
class AddMemberUseCase:
    """CU-05 - Agregar un miembro a un grupo (solo el anfitrion)."""

    member_repo: AbstractMemberRepository
    group_repo: AbstractGroupRepository

    async def execute(
        self,
        group_id: UUID,
        payload: AddMemberRequest,
        requester_id: UUID,
    ) -> MemberResponse:
        # Verify group exists
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")

        # Only host can add members
        if group.host_id != requester_id:
            raise ForbiddenError("Solo el anfitrion puede agregar miembros")

        # Check capacity
        active_count = await self.member_repo.count_active(group_id)
        if active_count >= group.max_members:
            raise ValueError("El grupo ya alcanzo el numero maximo de miembros")

        # Check duplicate
        existing = await self.member_repo.get_by_user_and_group(
            user_id=payload.user_id, group_id=group_id
        )
        if existing is not None:
            raise DuplicateEntityError("El usuario ya es miembro de este grupo")

        member = Member(group_id=group_id, user_id=payload.user_id)
        member.confirm()  # auto-confirm when host adds
        saved = await self.member_repo.create(member)
        return _to_response(saved)


@dataclass
class ListMembersUseCase:
    """CU-06 - Listar todos los miembros de un grupo."""

    member_repo: AbstractMemberRepository
    group_repo: AbstractGroupRepository

    async def execute(self, group_id: UUID) -> list[MemberResponse]:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        members = await self.member_repo.get_by_group(group_id)
        return [_to_response(m) for m in members]


@dataclass
class RemoveMemberUseCase:
    """Remove a member from a group (host only)."""

    member_repo: AbstractMemberRepository
    group_repo: AbstractGroupRepository

    async def execute(
        self, group_id: UUID, member_id: UUID, requester_id: UUID
    ) -> None:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        if group.host_id != requester_id:
            raise ForbiddenError("Solo el anfitrion puede eliminar miembros")
        member = await self.member_repo.get_by_id(member_id)
        if member is None:
            raise NotFoundError("Miembro no encontrado")
        await self.member_repo.delete(member_id)


__all__ = ["AddMemberUseCase", "ListMembersUseCase", "RemoveMemberUseCase"]
