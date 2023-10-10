import pytest
from httpx import AsyncClient


# Normal python function, just to help the tests.
async def create_post(body: str, async_client: AsyncClient) -> dict:
    """Creates a post and returns it."""
    response = await async_client.post(
        "/post",
        # Also sets the Header and content type:
        json={"body": body},
    )
    return response.json()


@pytest.fixture()
# creatED, because by the time the function runs, the post is already created.
async def created_post(async_client: AsyncClient):
    """Creates a post and returns it."""
    return await create_post("Test Post", async_client)


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    """Test that we can create a post."""
    body = "Test Post"

    response = await async_client.post(
        "/post",
        json={"body": body},
    )

    assert response.status_code == 201
    assert {"id": 0, "body": body}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient):
    """Test that we can't create a post without a body."""
    response = await async_client.post(
        "/post",
        json={},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    """Test that we can get all posts."""
    response = await async_client.get("/posts")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert created_post.items() <= response.json()[0].items()
    assert [created_post] == response.json()
