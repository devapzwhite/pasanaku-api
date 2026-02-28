"""Rounds API router - endpoints for round/turn management."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.dependencies import CurrentUserID, DBSession
from app.modules.groups.infrastructure.repositories import SQLAlchemyGroupRepository
from app.modules.rounds.application.schemas import CreateRoundRequest, RoundResponse
from app.modules.rounds.application.use_cases import (
    CreateRoundUseCase,
    GetRoundUseCase,
    ListRoundsUseCase,
    UpdateRoundStatusUseCase,
)
from app.modules.rounds.infrastructure.repositories import SQLAlchemyRoundRepository
from app.shared.exceptions import ForbiddenError, NotFoundError

router = APIRouter()


class UpdateStatusRequest(BaseModel):
    status: str


def _repos(db: DBSession):
    return (
        SQLAlchemyRoundRepository(session=db),
        SQLAlchemyGroupRepository(session=db),
    )


@router.post(
    "/{group_id}/rounds",
    response_model=RoundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CU-07 Crear ronda del Pasanaku",
)
async def create_round(
    group_id: UUID,
    payload: CreateRoundRequest,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> RoundResponse:
    round_repo, group_repo = _repos(db)
    use_case = CreateRoundUseCase(round_repo=round_repo, group_repo=group_repo)
    try:
        return await use_case.execute(
            group_id=group_id, payload=payload, requester_id=current_user_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.get(
    "/{group_id}/rounds",
    response_model=list[RoundResponse],
    summary="CU-08 Listar rondas del grupo",
)
async def list_rounds(
    group_id: UUID,
    db: DBSession,
) -> list[RoundResponse]:
    round_repo, group_repo = _repos(db)
    use_case = ListRoundsUseCase(round_repo=round_repo, group_repo=group_repo)
    try:
        return await use_case.execute(group_id=group_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(
    "/{group_id}/rounds/{round_id}",
    response_model=RoundResponse,
    summary="Obtener detalle de una ronda",
)
async def get_round(
    group_id: UUID,
    round_id: UUID,
    db: DBSession,
) -> RoundResponse:
    round_repo, _ = _repos(db)
    use_case = GetRoundUseCase(round_repo=round_repo)
    try:
        return await use_case.execute(round_id=round_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.patch(
    "/{group_id}/rounds/{round_id}/status",
    response_model=RoundResponse,
    summary="Actualizar estado de una ronda (solo anfitrion)",
)
async def update_round_status(
    group_id: UUID,
    round_id: UUID,
    payload: UpdateStatusRequest,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> RoundResponse:
    round_repo, group_repo = _repos(db)
    use_case = UpdateRoundStatusUseCase(round_repo=round_repo, group_repo=group_repo)
    try:
        return await use_case.execute(
            group_id=group_id,
            round_id=round_id,
            new_status=payload.status,
            requester_id=current_user_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
