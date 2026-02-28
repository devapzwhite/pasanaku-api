"""Groups API router - HTTP layer for group management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUserID, DBSession
from app.modules.groups.application.schemas import (
    CreateGroupRequest,
    GroupResponse,
    UpdateGroupRequest,
)
from app.modules.groups.application.use_cases import (
    CreateGroupUseCase,
    DeleteGroupUseCase,
    GetGroupUseCase,
    ListActiveGroupsUseCase,
    UpdateGroupUseCase,
)
from app.modules.groups.infrastructure.repositories import SQLAlchemyGroupRepository
from app.shared.exceptions import ForbiddenError, NotFoundError

router = APIRouter()


def _get_group_repo(db: DBSession) -> SQLAlchemyGroupRepository:
    """Factory: build repository from injected session."""
    return SQLAlchemyGroupRepository(session=db)


@router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CU-02 Crear grupo Pasanaku",
)
async def create_group(
    payload: CreateGroupRequest,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> GroupResponse:
    repo = _get_group_repo(db)
    use_case = CreateGroupUseCase(group_repo=repo)
    return await use_case.execute(payload=payload, host_id=current_user_id)


@router.get(
    "/",
    response_model=list[GroupResponse],
    summary="CU-03 Listar grupos activos",
)
async def list_active_groups(
    db: DBSession,
) -> list[GroupResponse]:
    repo = _get_group_repo(db)
    use_case = ListActiveGroupsUseCase(group_repo=repo)
    return await use_case.execute()


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
    summary="CU-04 Obtener detalle de grupo",
)
async def get_group(
    group_id: UUID,
    db: DBSession,
) -> GroupResponse:
    repo = _get_group_repo(db)
    use_case = GetGroupUseCase(group_repo=repo)
    try:
        return await use_case.execute(group_id=group_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.patch(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Actualizar grupo (solo anfitron)",
)
async def update_group(
    group_id: UUID,
    payload: UpdateGroupRequest,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> GroupResponse:
    repo = _get_group_repo(db)
    use_case = UpdateGroupUseCase(group_repo=repo)
    try:
        return await use_case.execute(
            group_id=group_id, payload=payload, requester_id=current_user_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar grupo (solo anfitron)",
)
async def delete_group(
    group_id: UUID,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> None:
    repo = _get_group_repo(db)
    use_case = DeleteGroupUseCase(group_repo=repo)
    try:
        await use_case.execute(group_id=group_id, requester_id=current_user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
