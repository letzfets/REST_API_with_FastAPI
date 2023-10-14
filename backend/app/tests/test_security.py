import pytest
from app import security
from app.config import config
from jose import jwt


def test_access_token_expire_minutes():
    """Test that the access token expire time is 30 minutes."""
    assert security.access_token_expire_minutes() == 30


def test_create_access_token():
    """Test that we can create an access token."""
    token = security.create_access_token("123")
    assert {"sub": "123"}.items() <= jwt.decode(
        token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
    ).items()


def test_password_hashing():
    """Test that we can hash a password."""
    password = "1234"
    hashed_password = security.get_password_hash(password)
    assert security.verify_password(password, hashed_password)
    assert password != hashed_password


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


@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    """Test that we can authenticate a user."""
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    """Test that we cannot authenticate a nonexisting user."""
    with pytest.raises(Exception):
        await security.authenticate_user("test@example.net", "1234")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    """Test that we cannot authenticate a user with a wrong password."""
    with pytest.raises(Exception):
        await security.authenticate_user(registered_user["email"], "wrong password")
