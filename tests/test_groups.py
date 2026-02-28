"""Unit tests for the groups module use cases.

Uses in-memory test doubles (fakes) - no real DB required.
Follows Arrange-Act-Assert (AAA) pattern.

CU-02: Crear grupo Pasanaku
CU-03: Listar grupos disponibles
CU-04: Obtener detalle de un grupo
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.modules.groups.application.schemas import CreateGroupRequest, UpdateGroupRequest
from app.modules.groups.application.use_cases import (
    CreateGroupUseCase,
    DeleteGroupUseCase,
    GetGroupUseCase,
    ListActiveGroupsUseCase,
    UpdateGroupUseCase,
)
from app.modules.groups.domain.entities import Frequency, Group, GroupStatus
from app.shared.exceptions import ForbiddenError, NotFoundError


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def make_group(
    name: str = "Grupo Navidad",
    host_id: uuid.UUID | None = None,
    max_members: int = 10,
    status: GroupStatus = GroupStatus.ACTIVE,
) -> Group:
    """Build a minimal Group domain entity for testing."""
    return Group(
        id=uuid.uuid4(),
        name=name,
        description="Un grupo de ahorro",
        host_id=host_id or uuid.uuid4(),
        amount_per_member=500.0,
        frequency=Frequency.MONTHLY,
        max_members=max_members,
        status=status,
        start_date=datetime.now(timezone.utc),
    )


def make_group_repo(
    existing_group: Group | None = None,
    active_groups: list[Group] | None = None,
) -> AsyncMock:
    """Build a mock group repository."""
    repo = AsyncMock()
    repo.create.side_effect = lambda g: g
    repo.get_by_id.return_value = existing_group
    repo.get_all_active.return_value = active_groups or []
    repo.update.side_effect = lambda g: g
    repo.delete.return_value = None
    return repo


# ---------------------------------------------------------------------------
# CreateGroupUseCase tests (CU-02)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_group_success():
    """CU-02 - Host can create a new group successfully."""
    host_id = uuid.uuid4()
    repo = make_group_repo()
    use_case = CreateGroupUseCase(group_repo=repo)
    payload = CreateGroupRequest(
        name="Grupo Navidad",
        description="Ahorro para navidad",
        amount_per_member=500.0,
        frequency=Frequency.MONTHLY,
        max_members=10,
        start_date=datetime.now(timezone.utc),
    )
    response = await use_case.execute(payload, host_id=host_id)
    assert response.name == "Grupo Navidad"
    assert response.host_id == host_id
    assert response.status == GroupStatus.ACTIVE
    repo.create.assert_called_once()


# ---------------------------------------------------------------------------
# ListActiveGroupsUseCase tests (CU-03)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_active_groups_returns_all():
    """CU-03 - Should return all active groups."""
    groups = [make_group(name=f"Grupo {i}") for i in range(3)]
    repo = make_group_repo(active_groups=groups)
    use_case = ListActiveGroupsUseCase(group_repo=repo)
    result = await use_case.execute()
    assert len(result) == 3


@pytest.mark.asyncio
async def test_list_active_groups_empty():
    """CU-03 - Should return empty list when no active groups exist."""
    repo = make_group_repo(active_groups=[])
    use_case = ListActiveGroupsUseCase(group_repo=repo)
    result = await use_case.execute()
    assert result == []


# ---------------------------------------------------------------------------
# GetGroupUseCase tests (CU-04)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_group_success():
    """CU-04 - Should return group details when group exists."""
    group = make_group(name="Grupo Test")
    repo = make_group_repo(existing_group=group)
    use_case = GetGroupUseCase(group_repo=repo)
    response = await use_case.execute(group_id=group.id)
    assert response.id == group.id
    assert response.name == "Grupo Test"


@pytest.mark.asyncio
async def test_get_group_not_found_raises():
    """CU-04 - Should raise NotFoundError when group does not exist."""
    repo = make_group_repo(existing_group=None)
    use_case = GetGroupUseCase(group_repo=repo)
    with pytest.raises(NotFoundError):
        await use_case.execute(group_id=uuid.uuid4())


# ---------------------------------------------------------------------------
# UpdateGroupUseCase tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_group_success():
    """Host can update their group."""
    host_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    repo = make_group_repo(existing_group=group)
    use_case = UpdateGroupUseCase(group_repo=repo)
    payload = UpdateGroupRequest(name="Grupo Actualizado")
    response = await use_case.execute(
        group_id=group.id, payload=payload, requester_id=host_id
    )
    assert response.name == "Grupo Actualizado"


@pytest.mark.asyncio
async def test_update_group_not_host_raises():
    """Non-host cannot update a group."""
    host_id = uuid.uuid4()
    other_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    repo = make_group_repo(existing_group=group)
    use_case = UpdateGroupUseCase(group_repo=repo)
    payload = UpdateGroupRequest(name="Intento ilegal")
    with pytest.raises(ForbiddenError):
        await use_case.execute(
            group_id=group.id, payload=payload, requester_id=other_id
        )


# ---------------------------------------------------------------------------
# DeleteGroupUseCase tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_group_success():
    """Host can delete their group."""
    host_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    repo = make_group_repo(existing_group=group)
    use_case = DeleteGroupUseCase(group_repo=repo)
    await use_case.execute(group_id=group.id, requester_id=host_id)
    repo.delete.assert_called_once_with(group.id)


@pytest.mark.asyncio
async def test_delete_group_not_host_raises():
    """Non-host cannot delete a group."""
    host_id = uuid.uuid4()
    other_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    repo = make_group_repo(existing_group=group)
    use_case = DeleteGroupUseCase(group_repo=repo)
    with pytest.raises(ForbiddenError):
        await use_case.execute(group_id=group.id, requester_id=other_id)
    repo.delete.assert_not_called()
