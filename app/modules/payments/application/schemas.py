"""Pydantic schemas for the payments application layer."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.payments.domain.entities import PaymentStatus


class RegisterPaymentRequest(BaseModel):
    """CU-09 - Registrar pago de un miembro."""
    payer_id: UUID
    amount: float = Field(..., gt=0)


class PaymentResponse(BaseModel):
    id: UUID
    round_id: UUID
    payer_id: UUID
    amount: float
    status: PaymentStatus
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = ["RegisterPaymentRequest", "PaymentResponse"]
