import pytest
from app import security


def test_password_hashing():
    """Test that we can hash a password."""
    password = "1234"
    hashed_password = security.get_password_hash(password)
    assert security.verify_password(password, hashed_password)


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    """Test that we can get a user from the database."""
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    """Test that we get None when a user is not found."""
    user = await security.get_user("test@example.net")
    assert user is None
