from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.api.exceptions import register_exception_handlers
from src.api.items import router as items_router
from src.api.roles import router as roles_router
from src.api.users import router as users_router

def create_app() -> FastAPI:
    app = FastAPI(title="Items database")
    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(roles_router)
    app.include_router(items_router)
    return app