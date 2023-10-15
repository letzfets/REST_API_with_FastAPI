import pytest
from app import security
from app.config import config
from jose import jwt


def test_access_token_expire_minutes():
    """Test that the access token expire time is 30 minutes."""
    assert security.access_token_expire_minutes() == 30


def test_confirm_token_expire_minutes():
    """Test that the confirm token expire time is a day."""
    assert security.confirm_token_expire_minutes() == 60 * 24


def test_create_access_token():
    """Test that we can create an access token."""
    token = security.create_access_token("123")
    assert {"sub": "123", "type": "access"}.items() <= jwt.decode(
        token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
    ).items()


def test_create_confirm_token():
    """Test that we can create a confirmation token."""
    token = security.create_confirmation_token("123")
    assert {"sub": "123", "type": "confirmation"}.items() <= jwt.decode(
        token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
    ).items()


def test_get_subject_for_token_type_valid_confirmation():
    """Test that we can get the subject from a valid confirmation token."""
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    assert email == security.get_subject_for_token_type(token, "confirmation")


def test_get_subject_for_token_type_valid_access():
    """Test that we can get the subject from a valid access token."""
    email = "test@example.com"
    token = security.create_access_token(email)
    assert email == security.get_subject_for_token_type(token, "access")


def test_get_subject_for_token_type_expired(mocker):
    """Test that we cannot get the subject from an expired token."""
    mocker.patch("app.security.access_token_expire_minutes", return_value=-1)
    email = "test@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token has expired" in exc_info.value.detail


def test_get_subject_for_token_type_invalid_token():
    """Test that we cannot get the subject from an expired token."""
    token = "Invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Invalid token" in exc_info.value.detail


def test_get_subject_for_token_type_missing_sub():
    """Test that we cannot get the subject from a token without a sub field."""
    email = "test@example.com"
    token = security.create_access_token(email)
    payload = jwt.decode(token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM])
    del payload["sub"]
    token = jwt.encode(payload, key=config.SECRET_KEY, algorithm=config.ALGORITHM)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token is missing 'sub' field" in exc_info.value.detail


def test_get_subject_for_token_type_wrong_type():
    """Test that we cannot get the subject from a token with the wrong type."""
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token is of incorrect type, expected 'access" in exc_info.value.detail


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
async def test_authenticate_user(confirmed_user: dict):
    """Test that we can authenticate a user."""
    user = await security.authenticate_user(
        confirmed_user["email"], confirmed_user["password"]
    )
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    """Test that we cannot authenticate a nonexisting user."""
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.net", "1234")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    """Test that we cannot authenticate a user with a wrong password."""
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrong password")


@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):
    """Test that we can get the current user."""
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    """Test that we cannot get a user with an invalid token."""
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalid token")


@pytest.mark.anyio
async def test_get_current_user_wrong_type_token(registered_user: dict):
    """Test that we cannot get a user with the wrong type of token."""
    token = security.create_confirmation_token(registered_user["email"])

    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)
