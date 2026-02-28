"""Rounds domain entities.

A Round represents one cycle in the Pasanaku: one member receives the collected
pot. The turn_number identifies which member in the rotation is the beneficiary.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class RoundStatus(StrEnum):
    PENDING = "pending"       # not yet started
    IN_PROGRESS = "in_progress"  # collection period open
    COMPLETED = "completed"   # pot delivered
    SKIPPED = "skipped"       # beneficiary skipped


@dataclass
class Round:
    """A single turn/cycle within a Pasanaku group."""

    id: UUID = field(default_factory=uuid4)
    group_id: UUID = field(default_factory=uuid4)
    beneficiary_id: UUID = field(default_factory=uuid4)  # FK -> users.id
    turn_number: int = 1           # position in the rotation (1-based)
    due_date: date = field(default_factory=date.today)
    total_amount: float = 0.0      # expected total pot
    status: RoundStatus = RoundStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def start(self) -> None:
        self.status = RoundStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        self.status = RoundStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def skip(self) -> None:
        self.status = RoundStatus.SKIPPED
        self.updated_at = datetime.now(timezone.utc)


__all__ = ["Round", "RoundStatus"]
