"""Auth domain entities (pure Python - no DB or framework dependencies)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class UserRole(StrEnum):
    """Available roles in the Pasanaku system."""

    HOST = "host"
    PLAYER = "player"


@dataclass
class User:
    """User aggregate root - core domain entity.

    Represents an authenticated participant in the Pasanaku system.
    No ORM or framework dependencies here (pure domain).
    """

    id: UUID = field(default_factory=uuid4)
    full_name: str = ""
    email: str = ""
    phone: str = ""
    hashed_password: str = ""
    role: UserRole = UserRole.PLAYER
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def deactivate(self) -> None:
        """Mark the user as inactive (soft-delete)."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Re-activate a previously deactivated user."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

    def change_role(self, new_role: UserRole) -> None:
        """Update the user role."""
        self.role = new_role
        self.updated_at = datetime.now(timezone.utc)

    def is_host(self) -> bool:
        """Return True if the user has the HOST role."""
        return self.role == UserRole.HOST


__all__ = ["User", "UserRole"]
