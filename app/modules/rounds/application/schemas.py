"""Pydantic schemas for the rounds application layer."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.rounds.domain.entities import RoundStatus


class CreateRoundRequest(BaseModel):
    """CU-07 - Crear ronda del Pasanaku."""
    beneficiary_id: UUID
    turn_number: int = Field(..., gt=0)
    due_date: date
    total_amount: float = Field(..., gt=0)


class RoundResponse(BaseModel):
    id: UUID
    group_id: UUID
    beneficiary_id: UUID
    turn_number: int
    due_date: date
    total_amount: float
    status: RoundStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = ["CreateRoundRequest", "RoundResponse"]
