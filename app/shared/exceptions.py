"""Domain-level custom exceptions for Pasanaku API."""
from fastapi import HTTPException, status


class PasanakulException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundError(PasanakulException):
    """Raised when a requested entity does not exist in the database."""


class DuplicateEntityError(PasanakulException):
    """Raised when attempting to create a duplicate entity."""


class UnauthorizedError(PasanakulException):
    """Raised when a user lacks permission to perform an action."""


class InvalidCredentialsError(PasanakulException):
    """Raised when authentication credentials are invalid."""


class InactiveUserError(PasanakulException):
    """Raised when an inactive user attempts to authenticate."""


# ---------------------------------------------------------------------------
# HTTP exception factories (translate domain errors -> HTTP responses)
# ---------------------------------------------------------------------------

def not_found_exception(resource: str, identifier: str | int) -> HTTPException:
    """Return a 404 HTTPException with a descriptive message."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} with id '{identifier}' not found.",
    )


def conflict_exception(detail: str) -> HTTPException:
    """Return a 409 HTTPException for duplicate resource errors."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
    )


def unauthorized_exception(detail: str = "Unauthorized") -> HTTPException:
    """Return a 403 HTTPException."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


__all__ = [
    "PasanakulException",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "UnauthorizedError",
    "InvalidCredentialsError",
    "InactiveUserError",
    "not_found_exception",
    "conflict_exception",
    "unauthorized_exception",
]
