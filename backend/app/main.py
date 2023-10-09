from app.routers.post import router as post_router
from fastapi import FastAPI

app = FastAPI()

# Interesting with the prefix here: investigate that!
# app.include_router(post_router, prefix="/api/v1")
app.include_router(post_router)
