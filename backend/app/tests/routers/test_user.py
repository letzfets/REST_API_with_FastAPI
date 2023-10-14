import pytest
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
