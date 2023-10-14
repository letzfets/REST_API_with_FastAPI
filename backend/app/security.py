import logging

from app.database import database, user_table

logger = logging.getLogger(__name__)


async def get_user(email: str):
    """Gets a user from the database by email."""

    logger.debug("Fetching user with email", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result
