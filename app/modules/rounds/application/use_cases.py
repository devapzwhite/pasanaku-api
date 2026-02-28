"""Rounds use cases.

CU-07: Crear ronda del Pasanaku
CU-08: Listar rondas de un grupo
"""
from dataclasses import dataclass
from uuid import UUID

from app.modules.rounds.application.schemas import CreateRoundRequest, RoundResponse
from app.modules.rounds.domain.entities import Round
from app.modules.rounds.domain.repositories import AbstractRoundRepository
from app.modules.groups.domain.repositories import AbstractGroupRepository
from app.shared.exceptions import NotFoundError, ForbiddenError


def _to_response(r: Round) -> RoundResponse:
    return RoundResponse(
        id=r.id,
        group_id=r.group_id,
        beneficiary_id=r.beneficiary_id,
        turn_number=r.turn_number,
        due_date=r.due_date,
        total_amount=r.total_amount,
        status=r.status,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@dataclass
class CreateRoundUseCase:
    """CU-07 - Crear una ronda dentro de un grupo (solo anfitrion)."""

    round_repo: AbstractRoundRepository
    group_repo: AbstractGroupRepository

    async def execute(
        self, group_id: UUID, payload: CreateRoundRequest, requester_id: UUID
    ) -> RoundResponse:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        if group.host_id != requester_id:
            raise ForbiddenError("Solo el anfitrion puede crear rondas")

        round_ = Round(
            group_id=group_id,
            beneficiary_id=payload.beneficiary_id,
            turn_number=payload.turn_number,
            due_date=payload.due_date,
            total_amount=payload.total_amount,
        )
        saved = await self.round_repo.create(round_)
        return _to_response(saved)


@dataclass
class ListRoundsUseCase:
    """CU-08 - Listar todas las rondas de un grupo."""

    round_repo: AbstractRoundRepository
    group_repo: AbstractGroupRepository

    async def execute(self, group_id: UUID) -> list[RoundResponse]:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        rounds = await self.round_repo.get_by_group(group_id)
        return [_to_response(r) for r in rounds]


@dataclass
class GetRoundUseCase:
    round_repo: AbstractRoundRepository

    async def execute(self, round_id: UUID) -> RoundResponse:
        round_ = await self.round_repo.get_by_id(round_id)
        if round_ is None:
            raise NotFoundError("Ronda no encontrada")
        return _to_response(round_)


@dataclass
class UpdateRoundStatusUseCase:
    """Advance the status of a round (host only)."""

    round_repo: AbstractRoundRepository
    group_repo: AbstractGroupRepository

    async def execute(
        self, group_id: UUID, round_id: UUID, new_status: str, requester_id: UUID
    ) -> RoundResponse:
        from app.modules.rounds.domain.entities import RoundStatus
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundError("Grupo no encontrado")
        if group.host_id != requester_id:
            raise ForbiddenError("Solo el anfitrion puede actualizar rondas")
        round_ = await self.round_repo.get_by_id(round_id)
        if round_ is None:
            raise NotFoundError("Ronda no encontrada")
        status = RoundStatus(new_status)
        if status == RoundStatus.IN_PROGRESS:
            round_.start()
        elif status == RoundStatus.COMPLETED:
            round_.complete()
        elif status == RoundStatus.SKIPPED:
            round_.skip()
        saved = await self.round_repo.update(round_)
        return _to_response(saved)


__all__ = [
    "CreateRoundUseCase",
    "ListRoundsUseCase",
    "GetRoundUseCase",
    "UpdateRoundStatusUseCase",
]
