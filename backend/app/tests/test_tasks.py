import httpx
import pytest
from app.database import post_table
from app.tasks import (
    APIResponseError,
    _generate_cute_creature_api,
    generate_and_add_to_post,
    send_simple_email,
)
from databases import Database


@pytest.mark.anyio
async def test_send_simple_email(mock_httpx_client):
    """Tests the send_simple_email function."""
    await send_simple_email("test@example.com", "Test Subject", "Test Body")
    mock_httpx_client.post.assert_called()


@pytest.mark.anyio
async def test_send_simple_email_api_response_error(mock_httpx_client):
    """Tests the send_simple_email function raises APIResponseError when server not available."""
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=500, content="", request=httpx.Request("POST", "//")
    )

    with pytest.raises(APIResponseError):
        await send_simple_email("test@example.com", "Test Subject", "Test Body")


@pytest.mark.anyio
async def test_generate_cute_creature_api_success(mock_httpx_client):
    """Tests the _generate_cute_creature_api function."""
    json_data = {"output_url": "https://example.com/image.jpg"}

    mock_httpx_client.post.return_value = httpx.Response(
        status_code=200,
        json=json_data,
        request=httpx.Request("POST", "//"),
    )

    result = await _generate_cute_creature_api("A cat")
    assert result == json_data


@pytest.mark.anyio
async def test_generate_cute_creature_api_http_error(mock_httpx_client):
    """Tests the _generate_cute_creature_api function raises APIResponseError when server not available."""
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=500, content="", request=httpx.Request("POST", "//")
    )

    with pytest.raises(
        APIResponseError, match="API request failed with status code 500"
    ):
        await _generate_cute_creature_api("A cat")


@pytest.mark.anyio
async def test_generate_cute_creature_api_json_error(mock_httpx_client):
    """Tests the _generate_cute_creature_api function raises APIResponseError when server returns invalid JSON."""
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=200, content="Not JSON", request=httpx.Request("POST", "//")
    )

    with pytest.raises(APIResponseError, match="API response could not be decoded"):
        await _generate_cute_creature_api("A cat")


@pytest.mark.anyio
async def test_generate_and_add_to_post(
    mock_httpx_client, created_post: dict, confirmed_user: dict, db: Database
):
    """Tests the generate_and_add_to_post function."""
    json_data = {"output_url": "https://example.com/image.jpg"}

    mock_httpx_client.post.return_value = httpx.Response(
        status_code=200,
        json=json_data,
        request=httpx.Request("POST", "//"),
    )
    await generate_and_add_to_post(
        confirmed_user["email"], created_post["id"], "/post/1", db, "A cat"
    )
    query = post_table.select().where(post_table.c.id == created_post["id"])
    updated_post = await db.fetch_one(query)
    assert updated_post.image_url == json_data["output_url"]
