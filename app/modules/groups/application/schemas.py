"""Pydantic schemas for the groups application layer."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.modules.groups.domain.entities import Frequency, GroupStatus


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CreateGroupRequest(BaseModel):
    """CU-02 - Crear grupo Pasanaku."""

    name: str = Field(..., min_length=3, max_length=100, examples=["Grupo Navidad"])
    description: str = Field(default="", max_length=500)
    amount_per_member: float = Field(..., gt=0, examples=[500.0])
    frequency: Frequency = Field(default=Frequency.MONTHLY)
    max_members: int = Field(..., gt=1, le=50, examples=[10])
    start_date: datetime

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del grupo no puede estar vacio")
        return v.strip()


class UpdateGroupRequest(BaseModel):
    """Partial update for a group."""

    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    amount_per_member: float | None = Field(default=None, gt=0)
    frequency: Frequency | None = None
    max_members: int | None = Field(default=None, gt=1, le=50)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class GroupResponse(BaseModel):
    """Full group representation returned by the API."""

    id: UUID
    name: str
    description: str
    host_id: UUID
    amount_per_member: float
    frequency: Frequency
    max_members: int
    status: GroupStatus
    start_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = [
    "CreateGroupRequest",
    "UpdateGroupRequest",
    "GroupResponse",
]
