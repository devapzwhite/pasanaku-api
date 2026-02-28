"""Unit tests for the auth module use cases.

Uses in-memory test doubles (fakes) - no real DB required.
Follows Arrange-Act-Assert (AAA) pattern.
"""
import uuid
from unittest.mock import AsyncMock

import pytest

from app.modules.auth.application.schemas import LoginRequest, RegisterRequest
from app.modules.auth.application.use_cases import LoginUseCase, RegisterUseCase
from app.modules.auth.domain.entities import User, UserRole
from app.shared.exceptions import DuplicateEntityError, InvalidCredentialsError


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def make_user(
    email: str = "test@example.com",
    role: UserRole = UserRole.PLAYER,
    is_active: bool = True,
) -> User:
    """Build a minimal User domain entity for testing."""
    from app.core.security import password_manager

    return User(
        id=uuid.uuid4(),
        full_name="Test User",
        email=email,
        phone="+591 70000000",
        hashed_password=password_manager.hash("password123"),
        role=role,
        is_active=is_active,
    )


def make_repo(
    email_exists: bool = False,
    existing_user: User | None = None,
) -> AsyncMock:
    """Build a mock repository."""
    repo = AsyncMock()
    repo.email_exists.return_value = email_exists
    repo.create.side_effect = lambda user: user  # return the same entity
    repo.get_by_email.return_value = existing_user
    return repo


# ---------------------------------------------------------------------------
# RegisterUseCase tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_success():
    """A new user with unique email should be created successfully."""
    repo = make_repo(email_exists=False)
    use_case = RegisterUseCase(user_repo=repo)

    payload = RegisterRequest(
        full_name="Juan Perez",
        email="juan@example.com",
        phone="+591 70000000",
        password="securepass123",
        confirm_password="securepass123",
        role=UserRole.PLAYER,
    )

    response = await use_case.execute(payload)

    assert response.user.email == "juan@example.com"
    assert response.user.role == UserRole.PLAYER
    assert response.user.is_active is True
    repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_duplicate_email_raises():
    """Registering with an existing email should raise DuplicateEntityError."""
    repo = make_repo(email_exists=True)
    use_case = RegisterUseCase(user_repo=repo)

    payload = RegisterRequest(
        full_name="Juan Perez",
        email="existing@example.com",
        phone="+591 70000000",
        password="securepass123",
        confirm_password="securepass123",
    )

    with pytest.raises(DuplicateEntityError):
        await use_case.execute(payload)

    repo.create.assert_not_called()


# ---------------------------------------------------------------------------
# LoginUseCase tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success():
    """Valid credentials should return JWT tokens."""
    user = make_user(email="player@example.com")
    repo = make_repo(existing_user=user)
    use_case = LoginUseCase(user_repo=repo)

    payload = LoginRequest(email="player@example.com", password="password123")
    response = await use_case.execute(payload)

    assert response.access_token
    assert response.refresh_token
    assert response.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_raises():
    """Wrong password should raise InvalidCredentialsError."""
    user = make_user()
    repo = make_repo(existing_user=user)
    use_case = LoginUseCase(user_repo=repo)

    payload = LoginRequest(email=user.email, password="wrongpassword")

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(payload)


@pytest.mark.asyncio
async def test_login_user_not_found_raises():
    """Login with non-existent email should raise InvalidCredentialsError."""
    repo = make_repo(existing_user=None)
    use_case = LoginUseCase(user_repo=repo)

    payload = LoginRequest(email="ghost@example.com", password="any")

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(payload)


@pytest.mark.asyncio
async def test_login_inactive_user_raises():
    """Inactive user should raise InactiveUserError on login attempt."""
    from app.shared.exceptions import InactiveUserError

    user = make_user(is_active=False)
    repo = make_repo(existing_user=user)
    use_case = LoginUseCase(user_repo=repo)

    payload = LoginRequest(email=user.email, password="password123")

    with pytest.raises(InactiveUserError):
        await use_case.execute(payload)
