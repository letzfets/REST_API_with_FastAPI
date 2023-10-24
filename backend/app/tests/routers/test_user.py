import pytest
from fastapi import BackgroundTasks
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    """Registers a user and returns it."""
    user_details = {"email": email, "password": password}
    user = await async_client.post("/register", json=user_details)
    return user


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    """Test that we can register a user."""
    response = await register_user(async_client, "test@example.com", "1234")
    assert response.status_code == 201
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
# the registered_user fixture is used here in the arguments
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    """Test that we cannot register a user twice."""
    response = await register_user(
        async_client, registered_user["email"], registered_user["password"]
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_confirm_user(async_client: AsyncClient, mocker):
    """Test that we can confirm a user."""
    spy = mocker.spy(BackgroundTasks, "add_task")
    await register_user(async_client, "test@example.com", "1234")
    confirmation_url = str(spy.call_args[0][3])
    response = await async_client.get(confirmation_url)
    assert response.status_code == 200
    assert "User confirmed" in response.json()["detail"]


@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    """Test that we cannot confirm a user with an invalid token."""
    response = await async_client.get("/confirm/invalidtoken")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    """Test that we can confirm a user."""
    mocker.patch("app.security.confirm_token_expire_minutes", return_value=-1)
    spy = mocker.spy(BackgroundTasks, "add_task")
    await register_user(async_client, "test@example.com", "1234")
    confirmation_url = str(spy.call_args[0][3])
    response = await async_client.get(confirmation_url)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    """Test that we cannot login a user that does not exist."""
    user_details = {"username": "test@example.net", "password": "1234"}
    response = await async_client.post("/token", data=user_details)
    assert response.status_code == 401
    assert "Invalid email or password." in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, confirmed_user: dict):
    """Test that we cannot login a user that does not exist."""
    response = await async_client.post(
        "/token",
        data={
            "username": confirmed_user["email"],
            "password": confirmed_user["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_login_user_note_confirmed(
    async_client: AsyncClient, registered_user: dict
):
    """Test that we cannot login a user that is not confirmed."""
    response = await async_client.post(
        "/token",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 401
    assert "Email not confirmed." in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_wrong_password(
    async_client: AsyncClient, confirmed_user: dict
):
    """Test that we cannot login a user with a wrong password."""
    response = await async_client.post(
        "/token",
        data={
            "username": confirmed_user["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Invalid email or password." in response.json()["detail"]
