"""Unit tests for the payments module use cases.

Uses in-memory test doubles (fakes) - no real DB required.
Follows Arrange-Act-Assert (AAA) pattern.

CU-09: Registrar pago de un miembro
CU-10: Listar pagos de una ronda
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.modules.payments.application.schemas import RegisterPaymentRequest
from app.modules.payments.application.use_cases import (
    ListPaymentsUseCase,
    RegisterPaymentUseCase,
)
from app.modules.payments.domain.entities import Payment, PaymentStatus
from app.modules.rounds.domain.entities import Round, RoundStatus
from app.shared.exceptions import DuplicateEntityError, NotFoundError


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def make_round(
    round_id: uuid.UUID | None = None,
    status: RoundStatus = RoundStatus.IN_PROGRESS,
) -> Round:
    """Build a minimal Round domain entity for testing."""
    from datetime import date
    return Round(
        id=round_id or uuid.uuid4(),
        group_id=uuid.uuid4(),
        beneficiary_id=uuid.uuid4(),
        turn_number=1,
        due_date=date.today(),
        total_amount=5000.0,
        status=status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_payment(
    round_id: uuid.UUID | None = None,
    payer_id: uuid.UUID | None = None,
) -> Payment:
    """Build a minimal Payment domain entity for testing."""
    return Payment(
        id=uuid.uuid4(),
        round_id=round_id or uuid.uuid4(),
        payer_id=payer_id or uuid.uuid4(),
        amount=500.0,
        status=PaymentStatus.CONFIRMED,
        paid_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_round_repo(
    existing_round: Round | None = None,
) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id.return_value = existing_round
    return repo


def make_payment_repo(
    existing_payment: Payment | None = None,
    payments: list[Payment] | None = None,
) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_payer_and_round.return_value = existing_payment
    repo.get_by_round.return_value = payments or []
    repo.create.side_effect = lambda p: p
    return repo


# ---------------------------------------------------------------------------
# RegisterPaymentUseCase tests (CU-09)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_payment_success():
    """CU-09 - Member can register a payment for a round."""
    payer_id = uuid.uuid4()
    round_ = make_round()
    round_repo = make_round_repo(existing_round=round_)
    payment_repo = make_payment_repo(existing_payment=None)
    use_case = RegisterPaymentUseCase(
        payment_repo=payment_repo, round_repo=round_repo
    )
    payload = RegisterPaymentRequest(payer_id=payer_id, amount=500.0)
    response = await use_case.execute(
        round_id=round_.id, payload=payload, requester_id=payer_id
    )
    assert response.round_id == round_.id
    assert response.payer_id == payer_id
    assert response.status == PaymentStatus.CONFIRMED
    payment_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_payment_round_not_found_raises():
    """CU-09 - Raises NotFoundError if round does not exist."""
    round_repo = make_round_repo(existing_round=None)
    payment_repo = make_payment_repo()
    use_case = RegisterPaymentUseCase(
        payment_repo=payment_repo, round_repo=round_repo
    )
    payload = RegisterPaymentRequest(payer_id=uuid.uuid4(), amount=500.0)
    with pytest.raises(NotFoundError):
        await use_case.execute(
            round_id=uuid.uuid4(), payload=payload, requester_id=uuid.uuid4()
        )
    payment_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_register_payment_duplicate_raises():
    """CU-09 - Duplicate payment for same payer and round raises DuplicateEntityError."""
    payer_id = uuid.uuid4()
    round_ = make_round()
    existing_payment = make_payment(round_id=round_.id, payer_id=payer_id)
    round_repo = make_round_repo(existing_round=round_)
    payment_repo = make_payment_repo(existing_payment=existing_payment)
    use_case = RegisterPaymentUseCase(
        payment_repo=payment_repo, round_repo=round_repo
    )
    payload = RegisterPaymentRequest(payer_id=payer_id, amount=500.0)
    with pytest.raises(DuplicateEntityError):
        await use_case.execute(
            round_id=round_.id, payload=payload, requester_id=payer_id
        )
    payment_repo.create.assert_not_called()


# ---------------------------------------------------------------------------
# ListPaymentsUseCase tests (CU-10)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_payments_success():
    """CU-10 - Should return all payments for a round."""
    round_ = make_round()
    payments = [make_payment(round_id=round_.id) for _ in range(4)]
    round_repo = make_round_repo(existing_round=round_)
    payment_repo = make_payment_repo(payments=payments)
    use_case = ListPaymentsUseCase(
        payment_repo=payment_repo, round_repo=round_repo
    )
    result = await use_case.execute(round_id=round_.id)
    assert len(result) == 4


@pytest.mark.asyncio
async def test_list_payments_empty():
    """CU-10 - Should return empty list when no payments exist."""
    round_ = make_round()
    round_repo = make_round_repo(existing_round=round_)
    payment_repo = make_payment_repo(payments=[])
    use_case = ListPaymentsUseCase(
        payment_repo=payment_repo, round_repo=round_repo
    )
    result = await use_case.execute(round_id=round_.id)
    assert result == []


@pytest.mark.asyncio
async def test_list_payments_round_not_found_raises():
    """CU-10 - Raises NotFoundError if round does not exist."""
    round_repo = make_round_repo(existing_round=None)
    payment_repo = make_payment_repo()
    use_case = ListPaymentsUseCase(
        payment_repo=payment_repo, round_repo=round_repo
    )
    with pytest.raises(NotFoundError):
        await use_case.execute(round_id=uuid.uuid4())
