import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest

os.environ["ENV_STATE"] = "test"  # noqa: E402
from app.database import database, user_table  # noqa: E402
from app.main import app
from app.tests.helpers import create_post  # noqa: E402
from fastapi.testclient import TestClient
from httpx import AsyncClient, Request, Response


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
    yield database
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
async def confirmed_user(registered_user: dict) -> dict:
    """Returns a confirmed user."""
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    """Returns a logged in user token."""
    response = await async_client.post("/token", json=confirmed_user)
    return response.json()["access_token"]


@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    """Mocks the send_email function."""
    mocked_client = mocker.patch("app.tasks.httpx.AsyncClient")

    mocked_async_client = Mock()
    response = Response(200, content="", request=Request("POST", "//"))
    mocked_async_client.post = AsyncMock(return_value=response)
    # __aenter__ is the method when calling a function asynchroniously
    # as
    mocked_client.return_value.__aenter__.return_value = mocked_async_client

    return mocked_async_client


@pytest.fixture()
# creatED, because by the time the function runs, the post is already created.
async def created_post(async_client: AsyncClient, logged_in_token: str):
    """Creates a post and returns it."""
    return await create_post("Test Post", async_client, logged_in_token)
