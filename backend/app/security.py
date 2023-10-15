import datetime
import logging
from typing import Annotated

from app.config import config
from app.database import database, user_table
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# smarter tokenUrl: /api/v1/user/token
# 1. populates the OpenAPI docs with the correct URL
# 2. when calling oauth2_scheme, it will automatically return the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def access_token_expire_minutes() -> str:
    """Returns the access token expire time in minutes."""
    return 30


def create_access_token(email: dict):
    """Creates an access token."""
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_payload = {
        "sub": email,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(
        jwt_payload, key=config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    """Gets a user from the database by email."""

    logger.debug("Fetching user with email", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result


async def authenticate_user(email: str, password: str):
    """Authenticates a user."""
    logger.debug("Authenticating user with email", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise credentials_exception
    # note, user.password is the hashed password!
    if not verify_password(password, user.password):
        raise credentials_exception
    return user


# The way arguments are past here is a dependency injection.
# That means token now depends on oauth2_scheme.
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Gets the current user from the database."""
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credentials_exception from e
    user = await get_user(email)
    if user is None:
        raise credentials_exception
    return user
