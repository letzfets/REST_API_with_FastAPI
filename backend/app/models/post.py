from pydantic import BaseModel


class UserPostIn(BaseModel):
    """This is the UserPostIn model"""

    body: str


class UserPost(UserPostIn):
    """This is the UserPost model"""

    id: int
