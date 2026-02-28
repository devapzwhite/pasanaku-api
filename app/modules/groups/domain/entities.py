"""Groups domain entities (pure Python - no DB or framework dependencies)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class GroupStatus(StrEnum):
    """Lifecycle states of a Pasanaku group."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Frequency(StrEnum):
    """Payment / draw frequency for the group."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


@dataclass
class Group:
    """Aggregate root for a Pasanaku savings group.

    A Pasanaku is a rotating savings club: members contribute a fixed
    amount each period and one member receives the whole pot per turn.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    host_id: UUID = field(default_factory=uuid4)  # FK -> users.id
    amount_per_member: float = 0.0
    frequency: Frequency = Frequency.MONTHLY
    max_members: int = 0
    status: GroupStatus = GroupStatus.ACTIVE
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def cancel(self) -> None:
        """Cancel the group, preventing new activity."""
        self.status = GroupStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        """Mark the group as completed after all rounds finish."""
        self.status = GroupStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def is_active(self) -> bool:
        """Return True if the group can still accept activity."""
        return self.status == GroupStatus.ACTIVE


__all__ = ["Group", "GroupStatus", "Frequency"]
