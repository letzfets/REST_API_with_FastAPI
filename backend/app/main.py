import logging
from contextlib import asynccontextmanager

from app.database import database
from app.logging_config import configure_logging

# from app.routers.docs import router as docs_router
from app.routers.post import router as post_router
from app.routers.upload import router as upload_router
from app.routers.user import router as user_router
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

# from fastapi.openapi.models import OAuthFlows, SecurityRequirement, SecurityScheme

logger = logging.getLogger(__name__)


# context manager does setup and tear down
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Awaits the database when the app starts and disconnects when it stops."""
    configure_logging()
    # logger.info("Hello world.")
    # logger.info("Hello world.")
    # logger.info("Hello world.")
    # logger.info("Hello world.")
    # logger.info("Hello world.")
    await database.connect()
    yield  # this is where the FastAPI runs - when its done, it comes back here and closes down
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

# Interesting with the prefix here: investigate that!
# app.include_router(post_router, prefix="/api/v1")
# app.include_router(docs_router)
app.include_router(post_router)
app.include_router(upload_router)
app.include_router(user_router)

# # Define the OAuth2 security scheme
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

# # Add the OAuth2 security scheme to the components section of the OpenAPI schema
# app.openapi()["components"]["securitySchemes"]["bearerAuth"] = oauth2_scheme

# # Add a security requirement to the OpenAPI schema that requires the "bearerAuth" security scheme
# security_requirement = SecurityRequirement(bearerAuth=["read", "write"])
# app.openapi()["security"].append(security_requirement)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Logs HTTPExceptions."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
