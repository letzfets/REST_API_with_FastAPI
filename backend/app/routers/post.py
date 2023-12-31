import logging
from enum import Enum
from typing import Annotated

import sqlalchemy
from app.database import comment_table, database, like_table, post_table
from app.models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
    UserPostWithLikes,
)
from app.models.user import User
from app.security import get_current_user
from app.tasks import generate_and_add_to_post
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.exceptions import HTTPException

router = APIRouter()

logger = logging.getLogger(__name__)


# @router.get("/")
# def read_root():
#     """This is the root path of the API"""
# return {"message": "Hello World"}


select_post_and_likes = (
    (
        sqlalchemy.select(
            post_table,
            sqlalchemy.func.count(like_table.c.id).label("likes"),
        )
    )
    .select_from(post_table.outerjoin(like_table))  # joins post_table with like_tables
    .group_by(
        post_table.c.id
    )  # and groups by post_table id => e.g. is a single row per post
)


async def find_post(post_id: int):
    """This is the find_post_by_id function"""
    logger.info(f"Finding post with id {post_id}")
    # generates a query clause
    # post_table.select() is equivalent to sqlalchemy.select([post_table]).select_from(post_table)
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)  # returns a SQLAlchemy Row object


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn,
    current_user: Annotated[User, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
    request: Request,
    prompt: str = None,
):
    """This is the create_post path of the API"""
    logger.info("Creating post")
    # following line protects the route
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)  # keys need to match columns in the table
    logger.debug(query)
    last_record_id = await database.execute(query)  # returns the id of the new record

    if prompt:
        background_tasks.add_task(
            generate_and_add_to_post,
            current_user.email,
            last_record_id,
            request.url_for("get_post_with_comments", post_id=last_record_id),
            database,
            prompt,
        )

    return {**data, "id": last_record_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


@router.get("/posts", response_model=list[UserPostWithLikes])
# FastAPI, knows that the PostSorting parameter is a query parameter,
# as it is of type Enum.
# http://api.com/posts?sorting=most_likes
async def get_all_posts(sorting: PostSorting = PostSorting.new):
    """This is returns all posts of the API"""
    logger.info("Getting all posts.")
    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))
    else:
        logger.error("Unknown sorting option", extra={"sorting": sorting})
    # Newer way in Python to do this:
    # match sorting:
    #     case PostSorting.new:
    #         query = select_post_and_likes.order_by(sqlalchemy.desc(post_table.c.id))
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
    # post = await find_post(post_id)
    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(query)
    post = await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }


@router.post("/post/{post_id}/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
):
    """This is the like_post path of the API"""
    logger.info("Liking post")
    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**like.model_dump(), "user_id": current_user.id}
    query = like_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
