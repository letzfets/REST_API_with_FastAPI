from app.models.post import UserPost, UserPostIn
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    """This is the root path of the API"""
    return {"message": "Hello World"}


# Database dummy in a dictionary:
post_table = {}


@router.post("/post", response_model=UserPost)
async def create_post(post: UserPostIn):
    """This is the create_post path of the API"""
    data = post.dict()
    last_record_id = len(post_table)
    new_post = {**data, "id": last_record_id}
    post_table[last_record_id] = new_post
    return new_post


@router.get("/posts", response_model=list[UserPost])
async def get_posts():
    """This is the get_posts path of the API"""
    return list(post_table.values())
