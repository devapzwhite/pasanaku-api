"""Payments use cases.

CU-09: Registrar pago de un miembro
CU-10: Listar pagos de una ronda
"""
from dataclasses import dataclass
from uuid import UUID

from app.modules.payments.application.schemas import (
    PaymentResponse,
    RegisterPaymentRequest,
)
from app.modules.payments.domain.entities import Payment
from app.modules.payments.domain.repositories import AbstractPaymentRepository
from app.modules.rounds.domain.repositories import AbstractRoundRepository
from app.shared.exceptions import DuplicateEntityError, ForbiddenError, NotFoundError


def _to_response(p: Payment) -> PaymentResponse:
    return PaymentResponse(
        id=p.id,
        round_id=p.round_id,
        payer_id=p.payer_id,
        amount=p.amount,
        status=p.status,
        paid_at=p.paid_at,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@dataclass
class RegisterPaymentUseCase:
    """CU-09 - Registrar el pago de un miembro para una ronda."""

    payment_repo: AbstractPaymentRepository
    round_repo: AbstractRoundRepository

    async def execute(
        self,
        round_id: UUID,
        payload: RegisterPaymentRequest,
        requester_id: UUID,
    ) -> PaymentResponse:
        round_ = await self.round_repo.get_by_id(round_id)
        if round_ is None:
            raise NotFoundError("Ronda no encontrada")

        # Check duplicate payment
        existing = await self.payment_repo.get_by_payer_and_round(
            payer_id=payload.payer_id, round_id=round_id
        )
        if existing is not None:
            raise DuplicateEntityError(
                "El miembro ya tiene un pago registrado para esta ronda"
            )

        payment = Payment(
            round_id=round_id,
            payer_id=payload.payer_id,
            amount=payload.amount,
        )
        payment.confirm()
        saved = await self.payment_repo.create(payment)
        return _to_response(saved)


@dataclass
class ListPaymentsUseCase:
    """CU-10 - Listar todos los pagos de una ronda."""

    payment_repo: AbstractPaymentRepository
    round_repo: AbstractRoundRepository

    async def execute(self, round_id: UUID) -> list[PaymentResponse]:
        round_ = await self.round_repo.get_by_id(round_id)
        if round_ is None:
            raise NotFoundError("Ronda no encontrada")
        payments = await self.payment_repo.get_by_round(round_id)
        return [_to_response(p) for p in payments]


__all__ = ["RegisterPaymentUseCase", "ListPaymentsUseCase"]
