from pydantic import BaseModel


class UserPostIn(BaseModel):
    """This is the UserPostIn model"""

    body: str


class UserPost(UserPostIn):
    """This is the UserPost model"""

    id: int


class CommentIn(BaseModel):
    """This is the Comment model"""

    body: str
    post_id: int


class Comment(CommentIn):
    """This is the Comment model"""

    id: int


class UserPostWithComments(BaseModel):
    """This is the UserPostWithComments model"""

    post: UserPost
    comments: list[Comment]
