"""Pydantic schemas for the members application layer."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.members.domain.entities import MemberStatus


class AddMemberRequest(BaseModel):
    """CU-05 - Agregar miembro a un grupo."""
    user_id: UUID


class MemberResponse(BaseModel):
    """Full member representation returned by the API."""
    id: UUID
    group_id: UUID
    user_id: UUID
    turn_number: int | None
    status: MemberStatus
    joined_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = ["AddMemberRequest", "MemberResponse"]
