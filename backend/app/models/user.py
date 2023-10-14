from pydantic import BaseModel


class User(BaseModel):
    """User model"""

    id: int | None = None
    email: str


class UserIn(User):
    """User model in"""

    password: str
