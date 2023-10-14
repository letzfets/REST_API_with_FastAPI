import logging

from app.database import database, user_table
from app.models.user import UserIn
from app.security import get_user
from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn):
    """This is the register path of the API"""
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )
    # TODO: hash the password!!!
    query = user_table.insert().values(email=user.email, password=user.password)
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User created"}
