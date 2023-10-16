import logging

from app import tasks
from app.database import database, user_table
from app.models.user import UserIn
from app.security import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_password_hash,
    get_subject_for_token_type,
    get_user,
)
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
    """This is the register path of the API"""
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)
    # fastapi will run the function in the background and automatically await it.
    # because this is the slow part of this function, background tasks, can run later
    # and the user will get the response from the register endpoint faster.
    # but don't use background tasks for things that are computational heavy.
    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email,
        request.url_for("confirm_email", token=create_confirmation_token(user.email)),
    )
    return {
        "detail": "User created. PLease confirm your email.",
    }


@router.post("/token")
async def login(user: UserIn):
    """This is the login path of the API"""
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    """This is the confirm path of the API"""
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )
    logger.debug(query)
    await database.execute(query)

    return {"detail": "User confirmed"}
