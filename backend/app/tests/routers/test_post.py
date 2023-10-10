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


async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    """Creates a post and returns it."""
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": post_id},
    )
    return response.json()


@pytest.fixture()
# creatED, because by the time the function runs, the post is already created.
async def created_post(async_client: AsyncClient):
    """Creates a post and returns it."""
    return await create_post("Test Post", async_client)


@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict):
    """Creates a comment and returns it."""
    return await create_comment("Test Comment", created_post["id"], async_client)


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


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    body = "Test Comment"

    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": created_post["id"]},
    )

    assert response.status_code == 201
    assert {
        "id": 0,
        "body": body,
        "post_id": created_post["id"],
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comment")

    assert response.status_code == 200
    assert response.json() == [created_comment]


@pytest.mark.anyio
async def test_get_comments_on_post_empty(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comment")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "post": created_post,
        "comments": [created_comment],
    }


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/post/2")

    assert response.status_code == 404
