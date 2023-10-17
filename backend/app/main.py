import logging
from contextlib import asynccontextmanager

from app.database import database
from app.logging_config import configure_logging
from app.routers.post import router as post_router
from app.routers.upload import router as upload_router
from app.routers.user import router as user_router
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

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
app.include_router(post_router)
app.include_router(upload_router)
app.include_router(user_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Logs HTTPExceptions."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
