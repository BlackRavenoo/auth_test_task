from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.domain.enums import ActionType, ResourceType
from src.services.auth import AuthService
from src.services.items import ItemService
from src.services.roles import RoleService
from src.services.users import UserService
from src.domain.entities.user import UserEntity
from src.domain.exceptions import ForbiddenException, UnauthorizedException
from src.domain.repositories.item import ItemRepository
from src.domain.repositories.role import RoleRepository
from src.domain.repositories.token import TokenRepository
from src.domain.repositories.user import UserRepository
from src.infra.repositories.item import SqlItemRepository
from src.infra.repositories.role import SqlRoleRepository
from src.infra.repositories.token import RedisTokenRepository
from src.infra.repositories.user import SqlUserRepository
from src.infra.session import get_async_session

async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> UserRepository:
    return SqlUserRepository(session)

async def get_role_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> RoleRepository:
    return SqlRoleRepository(session)

async def get_item_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> ItemRepository:
    return SqlItemRepository(session)

async def get_redis() -> aioredis.Redis:
    redis = await aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return redis

async def get_token_repository(
    redis: Annotated[aioredis.Redis, Depends(get_redis)]
) -> TokenRepository:
    return RedisTokenRepository(redis)

def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    token_repo: Annotated[TokenRepository, Depends(get_token_repository)]
) -> AuthService:
    return AuthService(user_repo, token_repo)

def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(user_repo)

def get_role_service(
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)]
) -> RoleService:
    return RoleService(role_repo)

def get_item_service(
    item_repo: Annotated[ItemRepository, Depends(get_item_repository)]
) -> ItemService:
    return ItemService(item_repo)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]

async def get_bearer_token(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if not authorization:
        raise UnauthorizedException("Missing authorization header")
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid authorization header")
    return authorization.split(" ", maxsplit=1)[1]

AccessTokenDep = Annotated[str, Depends(get_bearer_token)]

async def get_current_user(
    auth_service: AuthServiceDep,
    token: AccessTokenDep,
) -> UserEntity:
    return await auth_service.get_current_user(token)

def require_permission(resource: ResourceType, action: ActionType):
    async def check_permission(
        current_user: Annotated[UserEntity, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        service: RoleServiceDep,
    ) -> UserEntity:
        have_permission = await service.check_permission(current_user.role.id, resource, action)
        if not have_permission:
            raise ForbiddenException(f"You don't have permission to {action.value} {resource.value}")
        return current_user

    return check_permission

