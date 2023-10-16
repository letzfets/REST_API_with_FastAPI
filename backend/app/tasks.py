import logging

import httpx
from app.config import config


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
