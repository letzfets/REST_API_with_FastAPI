from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):
    """This is the UserPostIn model"""

    body: str


class UserPost(UserPostIn):
    """This is the UserPost model"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserPostWithLikes(UserPost):
    """This is the UserPostWithLikes model"""

    likes: int


class CommentIn(BaseModel):
    """This is the Comment model"""

    body: str
    post_id: int


class Comment(CommentIn):
    """This is the Comment model"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserPostWithComments(BaseModel):
    """This is the UserPostWithComments model"""

    post: UserPostWithLikes
    comments: list[Comment]


class PostLikeIn(BaseModel):
    """This is the PostLikeIn model"""

    post_id: int


class PostLike(PostLikeIn):
    """This is the PostLike model"""

    id: int
    user_id: int
