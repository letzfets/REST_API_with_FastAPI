from app.database import comment_table, database, post_table
from app.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

router = APIRouter()


@router.get("/")
def read_root():
    """This is the root path of the API"""
    return {"message": "Hello World"}


async def find_post(post_id: int):
    """This is the find_post_by_id function"""
    # generates a query clause
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)  # returns a SQLAlchemy Row object


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    """This is the create_post path of the API"""
    data = post.model_dump()
    query = post_table.insert().values(data)  # keys need to match columns in the table
    last_record_id = await database.execute(query)  # returns the id of the new record
    return {**data, "id": last_record_id}


@router.get("/posts", response_model=list[UserPost])
async def get_posts():
    """This is returns all posts of the API"""
    query = post_table.select()
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    """This is the create_comment path of the API"""
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    """This is the get_comments_on_post path of the API"""
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    """This is the get_post with comments path of the API"""
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
