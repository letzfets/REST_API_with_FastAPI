import pytest
from httpx import AsyncClient


# Normal python function, just to help the tests.
async def create_post(body: str, async_client: AsyncClient) -> dict:
    """Creates a post and returns it."""
    response = await async_client.post(
        "/post/",
        # Also sets the Header and content type:
        json={"body": body},
    )
    return response.json()


@pytest.fixture()
# creatED, because by the time the function runs, the post is already created.
async def created_post(async_client: AsyncClient):
    """Creates a post and returns it."""
    return await create_post("Test Post", async_client)
