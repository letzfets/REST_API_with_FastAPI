from contextlib import asynccontextmanager

from app.database import database
from app.routers.post import router as post_router
from fastapi import FastAPI


# context manager does setup and tear down
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Awaits the database when the app starts and disconnects when it stops."""
    await database.connect()
    yield  # this is where the FastAPI runs - when its done, it comes back here and closes down
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# Interesting with the prefix here: investigate that!
# app.include_router(post_router, prefix="/api/v1")
app.include_router(post_router)
