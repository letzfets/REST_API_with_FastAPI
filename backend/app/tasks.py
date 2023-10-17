import logging
from json import JSONDecodeError

import httpx
from app.config import config
from app.database import post_table
from databases import Database


class APIResponseError(Exception):
    """Raised when the API returns an error."""

    pass


logger = logging.getLogger(__name__)


async def send_simple_email(to: str, subject: str, body: str):
    """Sends a simple email through mailgun."""
    logger.debug(f"Sending email to {to} with subject {subject}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"Arnold Knott <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )
            response.raise_for_status()
            logger.debug(response.content)
        except httpx.HTTPError as e:
            raise APIResponseError(
                f"API request failed with status code {response.status_code}"
            ) from e


async def send_user_registration_email(email: str, confirmation_url: str):
    """Sends a user registration email."""
    await send_simple_email(
        email,
        "Successfully signed up",
        (
            f"Hi {email}! You have successfully signed up to the FastAPI demo project from udemy course"
            f"Please confirm your email by clicking on the following link: {confirmation_url}."
        ),
    )


async def _generate_cute_creature_api(prompt: str):
    """Generates a cute creature from a prompt using AI"""
    logger.debug("Generating cute creature")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.deepai.org/api/cute-creature-generator",
                data={"text": prompt},
                headers={"api-key": config.DEEPAI_API_KEY},
                timeout=60,
            )
            logger.debug(response)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as err:
            raise APIResponseError(
                f"API request failed with status code {err.response.status_code}"
            ) from err
        except (JSONDecodeError, TypeError) as err:
            raise APIResponseError("API response could not be decoded") from err


async def generate_and_add_to_post(
    email: str,
    post_id: str,
    post_url: str,
    database: Database,
    prompt: str = "A blue british shorthair cat is sitting on a couch.",
):
    """Generates a cute creature and adds it to a post."""
    try:
        response = await _generate_cute_creature_api(prompt)
    except APIResponseError:
        return await send_simple_email(
            email,
            "Error generating image",
            f"Hi {email}! Unfortunately there was an error generating an image"
            " for your post",
        )

    logger.debug("Connecting to database to update post image.")

    query = (
        post_table.update()
        .where(post_table.c.id == post_id)
        .values(image_url=response["output_url"])
    )

    logger.debug(query)

    await database.execute(query)

    logger.debug("Database connection in background task closed.")

    await send_simple_email(
        email,
        "Image generation completed",
        (
            f"Hi {email}! Your image has been generated and added to your post."
            f"Please click on the following link to view it: {post_url}."
        ),
    )
    return response
