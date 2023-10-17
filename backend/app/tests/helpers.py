from httpx import AsyncClient


# Normal python function, just to help the tests.
async def create_post(
    body: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    """Creates a post and returns it."""
    response = await async_client.post(
        "/post",
        # Also sets the Header and content type:
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def create_comment(
    body: str, post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    """Creates a post and returns it."""
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def like_post(
    post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    """Likes a post and returns it."""
    response = await async_client.post(
        f"/post/{post_id}/like",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()
