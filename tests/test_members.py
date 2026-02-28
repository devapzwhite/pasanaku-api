"""Unit tests for the members module use cases.

Uses in-memory test doubles (fakes) - no real DB required.
Follows Arrange-Act-Assert (AAA) pattern.

CU-05: Agregar miembro a un grupo
CU-06: Listar miembros de un grupo
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.modules.groups.domain.entities import Frequency, Group, GroupStatus
from app.modules.members.application.schemas import AddMemberRequest
from app.modules.members.application.use_cases import (
    AddMemberUseCase,
    ListMembersUseCase,
    RemoveMemberUseCase,
)
from app.modules.members.domain.entities import Member, MemberStatus
from app.shared.exceptions import DuplicateEntityError, ForbiddenError, NotFoundError


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def make_group(
    host_id: uuid.UUID | None = None,
    max_members: int = 10,
) -> Group:
    """Build a minimal Group domain entity for testing."""
    return Group(
        id=uuid.uuid4(),
        name="Grupo Test",
        description="Grupo para pruebas",
        host_id=host_id or uuid.uuid4(),
        amount_per_member=500.0,
        frequency=Frequency.MONTHLY,
        max_members=max_members,
        status=GroupStatus.ACTIVE,
        start_date=datetime.now(timezone.utc),
    )


def make_member(
    group_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> Member:
    """Build a minimal Member domain entity for testing."""
    return Member(
        id=uuid.uuid4(),
        group_id=group_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        status=MemberStatus.ACTIVE,
        joined_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_group_repo(group: Group | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = group
    return repo


def make_member_repo(
    existing_member: Member | None = None,
    members: list[Member] | None = None,
    active_count: int = 0,
) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_user_and_group.return_value = existing_member
    repo.get_by_group.return_value = members or []
    repo.count_active.return_value = active_count
    repo.create.side_effect = lambda m: m
    repo.get_by_id.return_value = existing_member
    repo.delete.return_value = None
    return repo


# ---------------------------------------------------------------------------
# AddMemberUseCase tests (CU-05)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_member_success():
    """CU-05 - Host can add a new member to their group."""
    host_id = uuid.uuid4()
    user_id = uuid.uuid4()
    group = make_group(host_id=host_id, max_members=5)
    group_repo = make_group_repo(group=group)
    member_repo = make_member_repo(existing_member=None, active_count=2)
    use_case = AddMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    payload = AddMemberRequest(user_id=user_id)
    response = await use_case.execute(
        group_id=group.id, payload=payload, requester_id=host_id
    )
    assert response.user_id == user_id
    assert response.group_id == group.id
    member_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_add_member_group_not_found_raises():
    """CU-05 - Raises NotFoundError if group does not exist."""
    group_repo = make_group_repo(group=None)
    member_repo = make_member_repo()
    use_case = AddMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    payload = AddMemberRequest(user_id=uuid.uuid4())
    with pytest.raises(NotFoundError):
        await use_case.execute(
            group_id=uuid.uuid4(), payload=payload, requester_id=uuid.uuid4()
        )
    member_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_add_member_not_host_raises():
    """CU-05 - Non-host cannot add members."""
    host_id = uuid.uuid4()
    other_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    group_repo = make_group_repo(group=group)
    member_repo = make_member_repo(active_count=0)
    use_case = AddMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    payload = AddMemberRequest(user_id=uuid.uuid4())
    with pytest.raises(ForbiddenError):
        await use_case.execute(
            group_id=group.id, payload=payload, requester_id=other_id
        )


@pytest.mark.asyncio
async def test_add_member_duplicate_raises():
    """CU-05 - Adding a user already in the group raises DuplicateEntityError."""
    host_id = uuid.uuid4()
    user_id = uuid.uuid4()
    group = make_group(host_id=host_id, max_members=10)
    existing_member = make_member(group_id=group.id, user_id=user_id)
    group_repo = make_group_repo(group=group)
    member_repo = make_member_repo(existing_member=existing_member, active_count=1)
    use_case = AddMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    payload = AddMemberRequest(user_id=user_id)
    with pytest.raises(DuplicateEntityError):
        await use_case.execute(
            group_id=group.id, payload=payload, requester_id=host_id
        )


@pytest.mark.asyncio
async def test_add_member_full_group_raises():
    """CU-05 - Adding member to a full group raises ValueError."""
    host_id = uuid.uuid4()
    group = make_group(host_id=host_id, max_members=2)
    group_repo = make_group_repo(group=group)
    member_repo = make_member_repo(existing_member=None, active_count=2)  # already full
    use_case = AddMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    payload = AddMemberRequest(user_id=uuid.uuid4())
    with pytest.raises(ValueError):
        await use_case.execute(
            group_id=group.id, payload=payload, requester_id=host_id
        )


# ---------------------------------------------------------------------------
# ListMembersUseCase tests (CU-06)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_members_success():
    """CU-06 - Should return all members of a group."""
    group = make_group()
    members = [make_member(group_id=group.id) for _ in range(3)]
    group_repo = make_group_repo(group=group)
    member_repo = make_member_repo(members=members)
    use_case = ListMembersUseCase(member_repo=member_repo, group_repo=group_repo)
    result = await use_case.execute(group_id=group.id)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_list_members_group_not_found_raises():
    """CU-06 - Raises NotFoundError if group does not exist."""
    group_repo = make_group_repo(group=None)
    member_repo = make_member_repo()
    use_case = ListMembersUseCase(member_repo=member_repo, group_repo=group_repo)
    with pytest.raises(NotFoundError):
        await use_case.execute(group_id=uuid.uuid4())


# ---------------------------------------------------------------------------
# RemoveMemberUseCase tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_remove_member_success():
    """Host can remove a member from their group."""
    host_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    member = make_member(group_id=group.id)
    group_repo = make_group_repo(group=group)
    member_repo = make_member_repo(existing_member=member)
    use_case = RemoveMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    await use_case.execute(
        group_id=group.id, member_id=member.id, requester_id=host_id
    )
    member_repo.delete.assert_called_once_with(member.id)


@pytest.mark.asyncio
async def test_remove_member_not_host_raises():
    """Non-host cannot remove members."""
    host_id = uuid.uuid4()
    other_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    member = make_member(group_id=group.id)
    group_repo = make_group_repo(group=group)
    member_repo = make_member_repo(existing_member=member)
    use_case = RemoveMemberUseCase(member_repo=member_repo, group_repo=group_repo)
    with pytest.raises(ForbiddenError):
        await use_case.execute(
            group_id=group.id, member_id=member.id, requester_id=other_id
        )
    member_repo.delete.assert_not_called()
