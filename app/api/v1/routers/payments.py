"""Payments API router - endpoints for payment registration."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUserID, DBSession
from app.modules.payments.application.schemas import (
    PaymentResponse,
    RegisterPaymentRequest,
)
from app.modules.payments.application.use_cases import (
    ListPaymentsUseCase,
    RegisterPaymentUseCase,
)
from app.modules.payments.infrastructure.repositories import SQLAlchemyPaymentRepository
from app.modules.rounds.infrastructure.repositories import SQLAlchemyRoundRepository
from app.shared.exceptions import DuplicateEntityError, NotFoundError

router = APIRouter()


def _repos(db: DBSession):
    return (
        SQLAlchemyPaymentRepository(session=db),
        SQLAlchemyRoundRepository(session=db),
    )


@router.post(
    "/{round_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CU-09 Registrar pago de un miembro",
)
async def register_payment(
    round_id: UUID,
    payload: RegisterPaymentRequest,
    current_user_id: CurrentUserID,
    db: DBSession,
) -> PaymentResponse:
    payment_repo, round_repo = _repos(db)
    use_case = RegisterPaymentUseCase(
        payment_repo=payment_repo, round_repo=round_repo
    )
    try:
        return await use_case.execute(
            round_id=round_id, payload=payload, requester_id=current_user_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except DuplicateEntityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.get(
    "/{round_id}/payments",
    response_model=list[PaymentResponse],
    summary="CU-10 Listar pagos de una ronda",
)
async def list_payments(
    round_id: UUID,
    db: DBSession,
) -> list[PaymentResponse]:
    payment_repo, round_repo = _repos(db)
    use_case = ListPaymentsUseCase(payment_repo=payment_repo, round_repo=round_repo)
    try:
        return await use_case.execute(round_id=round_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
