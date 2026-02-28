"""Payments domain entities.

A Payment records that a member has contributed their share
for a specific round within a Pasanaku group.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class PaymentStatus(StrEnum):
    PENDING = "pending"      # awaiting payment
    CONFIRMED = "confirmed"  # payment received and verified
    LATE = "late"            # payment received after due date
    MISSED = "missed"        # payment not made


@dataclass
class Payment:
    """Records a contribution by a member for a specific round."""

    id: UUID = field(default_factory=uuid4)
    round_id: UUID = field(default_factory=uuid4)
    payer_id: UUID = field(default_factory=uuid4)   # FK -> users.id
    amount: float = 0.0
    status: PaymentStatus = PaymentStatus.PENDING
    paid_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def confirm(self, paid_at: datetime | None = None) -> None:
        self.status = PaymentStatus.CONFIRMED
        self.paid_at = paid_at or datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_late(self, paid_at: datetime | None = None) -> None:
        self.status = PaymentStatus.LATE
        self.paid_at = paid_at or datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_missed(self) -> None:
        self.status = PaymentStatus.MISSED
        self.updated_at = datetime.now(timezone.utc)


__all__ = ["Payment", "PaymentStatus"]
