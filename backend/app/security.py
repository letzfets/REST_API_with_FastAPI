import datetime
import logging
from typing import Annotated, Literal

from app.config import config
from app.database import database, user_table
from fastapi import Depends, HTTPException, status

# from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

# from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

# from fastapi.openapi.models import OAuthFlows, SecurityScheme


logger = logging.getLogger(__name__)


# oauth2_scheme = SecurityScheme(
#     type="oauth2",
#     flows=OAuthFlows(
#         bearer={
#             "scheme": "bearer",
#             "bearerFormat": "JWT",
#             "tokenUrl": "/token",
#         }
#     ),
# )
# smarter tokenUrl: /api/v1/user/token
# 1. populates the OpenAPI docs with the correct URL
# 2. when calling oauth2_scheme, it will automatically return the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])


# def get_openapi_schema():
#     openapi_schema = get_openapi(
#         title="My API",
#         version="1.0.0",
#         description="My API description",
#         # routes=router.routes,
#     )
#     # Add the security requirement to the OpenAPI schema
#     openapi_schema["security"] = [{"oauth2": []}]
#     openapi_schema["components"] = {"securitySchemes": {"oauth2": oauth2_scheme}}
#     return openapi_schema


def create_credentials_exception(detail: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def access_token_expire_minutes() -> str:
    """Returns the access token expire time in minutes."""
    return 30


def confirm_token_expire_minutes() -> str:
    """Returns the confirm token expire time in minutes."""
    return 60 * 24


def create_access_token(email: dict):
    """Creates an access token."""
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_payload = {
        "sub": email,
        "exp": expire,
        "type": "access",  # to distinguish between access and confirm tokens
    }
    encoded_jwt = jwt.encode(
        jwt_payload, key=config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


def create_confirmation_token(email: dict):
    """Creates an confirmation token."""
    logger.debug("Creating confirmation token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=confirm_token_expire_minutes()
    )
    jwt_payload = {
        "sub": email,
        "exp": expire,
        "type": "confirmation",  # to distinguish between access and confirm tokens
    }
    encoded_jwt = jwt.encode(
        jwt_payload, key=config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


def get_subject_for_token_type(
    token: str, type: Literal["access", "confirmation"]
) -> str:
    if not token:
        raise create_credentials_exception("Token not present.")
    try:
        payload = jwt.decode(
            token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token has expired") from e
    except JWTError as e:
        raise create_credentials_exception("Invalid token") from e
    email = payload.get("sub")
    if email is None:
        raise create_credentials_exception("Token is missing 'sub' field")
    token_type = payload.get("type")
    if type is None or token_type != type:
        raise create_credentials_exception(
            f"Token is of incorrect type, expected '{type}'"
        )
    return email


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
        raise create_credentials_exception("Invalid email or password.")
    # note, user.password is the hashed password!
    if not verify_password(password, user.password):
        raise create_credentials_exception("Invalid email or password.")
    if not user.confirmed:
        raise create_credentials_exception("Email not confirmed.")
    return user


# The way arguments are past here is a dependency injection.
# That means token now depends on oauth2_scheme.
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Gets the current user from the database."""
    email = get_subject_for_token_type(token, "access")
    user = await get_user(email)
    if user is None:
        raise create_credentials_exception("User not found")
    return user
