"""Members domain entities."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class MemberStatus(StrEnum):
    """Membership status within a group."""
    PENDING = "pending"    # invited but not yet confirmed
    ACTIVE = "active"      # confirmed member
    REMOVED = "removed"    # removed from the group


@dataclass
class Member:
    """Represents the relationship between a user and a Pasanaku group."""

    id: UUID = field(default_factory=uuid4)
    group_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    turn_number: int | None = None   # assigned turn order (1-based)
    status: MemberStatus = MemberStatus.PENDING
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def confirm(self) -> None:
        """Confirm the membership invitation."""
        self.status = MemberStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)

    def remove(self) -> None:
        """Remove the member from the group."""
        self.status = MemberStatus.REMOVED
        self.updated_at = datetime.now(timezone.utc)


__all__ = ["Member", "MemberStatus"]
