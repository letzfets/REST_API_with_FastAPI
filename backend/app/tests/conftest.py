import os
from typing import AsyncGenerator, Generator

import pytest

os.environ["ENV_STATE"] = "test"  # noqa: E402
from app.database import database, user_table  # noqa: E402
from app.main import app
from fastapi.testclient import TestClient
from httpx import AsyncClient


# runs only once per test session
@pytest.fixture(scope="session")
def anyio_backend():
    """Use async io backend for pytest."""
    return "asyncio"


# defines the comming function as a fixture
@pytest.fixture()
def client() -> Generator:
    """Returns a TestClient instance."""
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> Generator:
    """Clears the database before each test."""
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
# As the argument is another fixture, pytest will run the client fixture first and then pass the result to async_client.
async def async_client(client) -> AsyncGenerator:
    """Returns an AsyncClient instance."""
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    """Creates a user and returns it."""
    user_details = {"email": "test@example.com", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, registered_user: dict) -> str:
    """Returns a logged in user token."""
    response = await async_client.post("/token", json=registered_user)
    return response.json()["access_token"]
