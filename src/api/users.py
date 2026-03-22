from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import AccessTokenDep, AuthServiceDep, get_current_user, get_user_service, require_permission
from src.domain.enums import ActionType, ResourceType
from src.services.users import UserService
from src.domain.entities.user import UserEntity
from src.schemas.auth import LogoutRequest
from src.schemas.user import UserCreate, UserFilter, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.USERS, ActionType.READ))],
    service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=100),
) -> list[UserEntity]:
    filters = UserFilter(page=page, page_size=page_size)
    return await service.get_all(filters)

@router.get("/{id:int}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    id: int,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.USERS, ActionType.READ))],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserEntity:
    return await service.get_by_id(id)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.USERS, ActionType.WRITE))],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserEntity:
    return await service.create(data)

@router.patch("/{id:int}", status_code=status.HTTP_200_OK)
async def update_user(
    id: int,
    data: UserUpdate,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.USERS, ActionType.WRITE))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    await service.update(id, data)


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_me(
    data: UserUpdate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserEntity:
    await service.update(current_user.id, data)
    return await service.get_by_id(current_user.id)

@router.delete("/{id:int}", status_code=status.HTTP_200_OK)
async def delete_user(
    id: int,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.USERS, ActionType.DELETE))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    await service.delete(id)


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    data: LogoutRequest,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    access_token: AccessTokenDep,
    service: Annotated[UserService, Depends(get_user_service)],
    auth_service: AuthServiceDep,
):
    await service.soft_delete(current_user.id)
    await auth_service.logout(data.refresh_token, access_token)
