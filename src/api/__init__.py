from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.api.exceptions import register_exception_handlers
from src.api.items import router as items_router
from src.api.roles import router as roles_router
from src.api.users import router as users_router
from src.config import settings

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        try:
            yield
        finally:
            await app.state.redis.aclose()

    app = FastAPI(title="Items database", lifespan=lifespan)
    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(roles_router)
    app.include_router(items_router)
    return app