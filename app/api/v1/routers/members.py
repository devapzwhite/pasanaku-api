"""Members API router - endpoints for group membership management."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUserID, DBSession
from app.modules.groups.infrastructure.repositories import SQLAlchemyGroupRepository
from app.modules.members.application.schemas import AddMemberRequest, MemberResponse
from app.modules.members.application.use_cases import (
    AddMemberUseCase,
    ListMembersUseCase,
    RemoveMemberUseCase,
)
from app.modules.members.infrastructure.repositories import SQLAlchemyMemberRepository
from app.shared.exceptions import DuplicateEntityError, ForbiddenError, NotFoundError

router = APIRouter()


def _repos(db: DBSession):
    return (
        SQLAlchemyMemberRepository(session=db),
        SQLAlchemyGroupRepository(session=db),
    )


@router.post(
    "/{group_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CU-05 Agregar miembro al grupo",
)
async def add_member(
    group_id: UUID,
    payload: AddMemberRequest,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> MemberResponse:
    member_repo, group_repo = _repos(db)
    use_case = AddMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    try:
        return await use_case.execute(
            group_id=group_id, payload=payload, requester_id=current_user_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except DuplicateEntityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{group_id}/members",
    response_model=list[MemberResponse],
    summary="CU-06 Listar miembros del grupo",
)
async def list_members(
    group_id: UUID,
    db: DBSession,
) -> list[MemberResponse]:
    member_repo, group_repo = _repos(db)
    use_case = ListMembersUseCase(member_repo=member_repo, group_repo=group_repo)
    try:
        return await use_case.execute(group_id=group_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete(
    "/{group_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar miembro del grupo (solo anfitrion)",
)
async def remove_member(
    group_id: UUID,
    member_id: UUID,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> None:
    member_repo, group_repo = _repos(db)
    use_case = RemoveMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    try:
        await use_case.execute(
            group_id=group_id, member_id=member_id, requester_id=current_user_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
