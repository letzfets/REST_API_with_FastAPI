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
# Database dummy in a dictionary:
post_table = {}
comment_table = {}


@router.get("/")
def read_root():
    """This is the root path of the API"""
    return {"message": "Hello World"}


def find_post(post_id: int):
    """This is the find_post_by_id function"""
    return post_table.get(post_id)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    """This is the create_post path of the API"""
    data = post.model_dump()
    last_record_id = len(post_table)
    new_post = {**data, "id": last_record_id}
    post_table[last_record_id] = new_post
    return new_post


@router.get("/posts", response_model=list[UserPost])
async def get_posts():
    """This is returns all posts of the API"""
    return list(post_table.values())


@router.post("/comment", response_model=Comment, status_code=201)
async def create_post(comment: CommentIn):
    """This is the create_post path of the API"""
    post = find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    last_record_id = len(comment_table)
    new_comment = {**data, "id": last_record_id}
    comment_table[last_record_id] = new_comment
    return new_comment


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    """This is the get_comments_on_post path of the API"""
    # this is a list comprehension:
    return [
        comment for comment in comment_table.values() if comment["post_id"] == post_id
    ]
    # post = find_post(post_id)
    # if not post:
    #     raise HTTPException(status_code=404, detail="Post not found")

    # return list(comment_table.values())


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    """This is the get_post with comments path of the API"""
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
