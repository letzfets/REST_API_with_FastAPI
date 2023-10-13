import os
from typing import AsyncGenerator, Generator

import pytest

os.environ["ENV_STATE"] = "test"  # noqa: E402
from app.main import app
from app.routers.post import comment_table, post_table
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
def db() -> Generator:
    """Clears the database before each test."""
    post_table.clear()
    comment_table.clear()
    yield


@pytest.fixture()
# As the argument is another fixture, pytest will run the client fixture first and then pass the result to async_client.
async def async_client(client) -> AsyncGenerator:
    """Returns an AsyncClient instance."""
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac
