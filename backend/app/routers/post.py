import logging
from typing import Annotated

from app.database import comment_table, database, post_table
from app.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)
from app.models.user import User
from app.security import get_current_user
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/")
def read_root():
    """This is the root path of the API"""
    return {"message": "Hello World"}


async def find_post(post_id: int):
    """This is the find_post_by_id function"""
    logger.info(f"Finding post with id {post_id}")
    # generates a query clause
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)  # returns a SQLAlchemy Row object


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
):
    """This is the create_post path of the API"""
    logger.info("Creating post")
    # following line protects the route
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)  # keys need to match columns in the table
    logger.debug(query)
    last_record_id = await database.execute(query)  # returns the id of the new record
    return {**data, "id": last_record_id}


@router.get("/posts", response_model=list[UserPost])
async def get_all_posts():
    """This is returns all posts of the API"""
    logger.info("Getting all posts.")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: Annotated[User, Depends(get_current_user)]
):
    """This is the create_comment path of the API"""
    logger.info("Creating comment on post")
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    # logger.debug(query, extra={"post_id": post.id, "email": "bob@example.com"})
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    """This is the get_comments_on_post path of the API"""
    logger.info(f"Getting comments on post with id {post_id}")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    """This is the get_post with comments path of the API"""
    logger.info(f"Getting post with id {post_id} and all its comments")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
