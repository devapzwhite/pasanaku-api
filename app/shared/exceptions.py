"""Domain-level custom exceptions for Pasanaku API."""
from fastapi import HTTPException, status


class PasanakuException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundError(PasanakuException):
    """Raised when a requested entity does not exist in the database."""


class DuplicateEntityError(PasanakuException):
    """Raised when attempting to create a duplicate entity."""


class UnauthorizedError(PasanakuException):
    """Raised when a user lacks permission to perform an action."""


class InvalidCredentialsError(PasanakuException):
    """Raised when authentication credentials are invalid."""


class InactiveUserError(PasanakuException):
    """Raised when an inactive user attempts to authenticate."""


class NotFoundError(EntityNotFoundError):
    """Alias for EntityNotFoundError - raised when a resource is not found."""


class ForbiddenError(UnauthorizedError):
    """Raised when a user is authenticated but lacks resource-level permission."""


# ------------------------------------------------------------------
# HTTP exception factories (translate domain errors -> HTTP responses)
# ------------------------------------------------------------------

def not_found_exception(resource: str, identifier: str | int) -> HTTPException:
    """Return a 404 HTTPException with a descriptive message."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} with id '{identifier}' not found.",
    )


def conflict_exception(detail: str) -> HTTPException:
    """Return a 409 HTTPException."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
    )


def forbidden_exception(detail: str) -> HTTPException:
    """Return a 403 HTTPException."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )
