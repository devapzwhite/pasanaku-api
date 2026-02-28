"""Unit tests for the rounds module use cases.

Uses in-memory test doubles (fakes) - no real DB required.
Follows Arrange-Act-Assert (AAA) pattern.

CU-07: Crear ronda del Pasanaku
CU-08: Listar rondas de un grupo
"""
import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.modules.groups.domain.entities import Frequency, Group, GroupStatus
from app.modules.rounds.application.schemas import CreateRoundRequest
from app.modules.rounds.application.use_cases import (
    CreateRoundUseCase,
    GetRoundUseCase,
    ListRoundsUseCase,
    UpdateRoundStatusUseCase,
)
from app.modules.rounds.domain.entities import Round, RoundStatus
from app.shared.exceptions import ForbiddenError, NotFoundError


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def make_group(
    host_id: uuid.UUID | None = None,
) -> Group:
    """Build a minimal Group domain entity for testing."""
    return Group(
        id=uuid.uuid4(),
        name="Grupo Test",
        description="Grupo para pruebas",
        host_id=host_id or uuid.uuid4(),
        amount_per_member=500.0,
        frequency=Frequency.MONTHLY,
        max_members=10,
        status=GroupStatus.ACTIVE,
        start_date=datetime.now(timezone.utc),
    )


def make_round(
    group_id: uuid.UUID | None = None,
    beneficiary_id: uuid.UUID | None = None,
    status: RoundStatus = RoundStatus.PENDING,
) -> Round:
    """Build a minimal Round domain entity for testing."""
    return Round(
        id=uuid.uuid4(),
        group_id=group_id or uuid.uuid4(),
        beneficiary_id=beneficiary_id or uuid.uuid4(),
        turn_number=1,
        due_date=date.today(),
        total_amount=5000.0,
        status=status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_group_repo(group: Group | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = group
    return repo


def make_round_repo(
    existing_round: Round | None = None,
    rounds: list[Round] | None = None,
) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = existing_round
    repo.get_by_group.return_value = rounds or []
    repo.create.side_effect = lambda r: r
    repo.update.side_effect = lambda r: r
    return repo


# ---------------------------------------------------------------------------
# CreateRoundUseCase tests (CU-07)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_round_success():
    """CU-07 - Host can create a round within their group."""
    host_id = uuid.uuid4()
    beneficiary_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    group_repo = make_group_repo(group=group)
    round_repo = make_round_repo()
    use_case = CreateRoundUseCase(round_repo=round_repo, group_repo=group_repo)
    payload = CreateRoundRequest(
        beneficiary_id=beneficiary_id,
        turn_number=1,
        due_date=date.today(),
        total_amount=5000.0,
    )
    response = await use_case.execute(
        group_id=group.id, payload=payload, requester_id=host_id
    )
    assert response.group_id == group.id
    assert response.beneficiary_id == beneficiary_id
    assert response.status == RoundStatus.PENDING
    round_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_round_group_not_found_raises():
    """CU-07 - Raises NotFoundError if group does not exist."""
    group_repo = make_group_repo(group=None)
    round_repo = make_round_repo()
    use_case = CreateRoundUseCase(round_repo=round_repo, group_repo=group_repo)
    payload = CreateRoundRequest(
        beneficiary_id=uuid.uuid4(),
        turn_number=1,
        due_date=date.today(),
        total_amount=5000.0,
    )
    with pytest.raises(NotFoundError):
        await use_case.execute(
            group_id=uuid.uuid4(), payload=payload, requester_id=uuid.uuid4()
        )
    round_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_round_not_host_raises():
    """CU-07 - Non-host cannot create rounds."""
    host_id = uuid.uuid4()
    other_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    group_repo = make_group_repo(group=group)
    round_repo = make_round_repo()
    use_case = CreateRoundUseCase(round_repo=round_repo, group_repo=group_repo)
    payload = CreateRoundRequest(
        beneficiary_id=uuid.uuid4(),
        turn_number=1,
        due_date=date.today(),
        total_amount=5000.0,
    )
    with pytest.raises(ForbiddenError):
        await use_case.execute(
            group_id=group.id, payload=payload, requester_id=other_id
        )


# ---------------------------------------------------------------------------
# ListRoundsUseCase tests (CU-08)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_rounds_success():
    """CU-08 - Should return all rounds of a group."""
    group = make_group()
    rounds = [make_round(group_id=group.id) for _ in range(3)]
    group_repo = make_group_repo(group=group)
    round_repo = make_round_repo(rounds=rounds)
    use_case = ListRoundsUseCase(round_repo=round_repo, group_repo=group_repo)
    result = await use_case.execute(group_id=group.id)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_list_rounds_group_not_found_raises():
    """CU-08 - Raises NotFoundError if group does not exist."""
    group_repo = make_group_repo(group=None)
    round_repo = make_round_repo()
    use_case = ListRoundsUseCase(round_repo=round_repo, group_repo=group_repo)
    with pytest.raises(NotFoundError):
        await use_case.execute(group_id=uuid.uuid4())


# ---------------------------------------------------------------------------
# GetRoundUseCase tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_round_success():
    """Should return round details when round exists."""
    round_ = make_round()
    round_repo = make_round_repo(existing_round=round_)
    use_case = GetRoundUseCase(round_repo=round_repo)
    response = await use_case.execute(round_id=round_.id)
    assert response.id == round_.id


@pytest.mark.asyncio
async def test_get_round_not_found_raises():
    """Should raise NotFoundError when round does not exist."""
    round_repo = make_round_repo(existing_round=None)
    use_case = GetRoundUseCase(round_repo=round_repo)
    with pytest.raises(NotFoundError):
        await use_case.execute(round_id=uuid.uuid4())


# ---------------------------------------------------------------------------
# UpdateRoundStatusUseCase tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_round_status_to_in_progress():
    """Host can advance a round to IN_PROGRESS."""
    host_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    round_ = make_round(group_id=group.id, status=RoundStatus.PENDING)
    group_repo = make_group_repo(group=group)
    round_repo = make_round_repo(existing_round=round_)
    use_case = UpdateRoundStatusUseCase(round_repo=round_repo, group_repo=group_repo)
    response = await use_case.execute(
        group_id=group.id,
        round_id=round_.id,
        new_status=RoundStatus.IN_PROGRESS,
        requester_id=host_id,
    )
    assert response.status == RoundStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_update_round_status_not_host_raises():
    """Non-host cannot update round status."""
    host_id = uuid.uuid4()
    other_id = uuid.uuid4()
    group = make_group(host_id=host_id)
    round_ = make_round(group_id=group.id)
    group_repo = make_group_repo(group=group)
    round_repo = make_round_repo(existing_round=round_)
    use_case = UpdateRoundStatusUseCase(round_repo=round_repo, group_repo=group_repo)
    with pytest.raises(ForbiddenError):
        await use_case.execute(
            group_id=group.id,
            round_id=round_.id,
            new_status=RoundStatus.IN_PROGRESS,
            requester_id=other_id,
        )
