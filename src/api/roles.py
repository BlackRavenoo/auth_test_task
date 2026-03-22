from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.deps import get_role_service, require_permission
from src.domain.enums import ActionType, ResourceType
from src.services.roles import RoleService
from src.domain.entities.role import RoleEntity
from src.domain.entities.user import UserEntity
from src.schemas.role import RoleCreate, RolePermissionResponse, RolePermissionUpdate, RoleResponse, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("", response_model=list[RoleResponse], status_code=status.HTTP_200_OK)
async def get_roles(
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ROLES, ActionType.READ))],
    service: Annotated[RoleService, Depends(get_role_service)],
) -> list[RoleEntity]:
    return await service.get_all()

@router.get("/{id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def get_role(
    id: int,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ROLES, ActionType.READ))],
    service: Annotated[RoleService, Depends(get_role_service)],
) -> RoleEntity:
    return await service.get_by_id(id)

@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ROLES, ActionType.WRITE))],
    service: Annotated[RoleService, Depends(get_role_service)],
) -> RoleEntity:
    return await service.create(data.name)

@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def update_role(
    id: int,
    data: RoleUpdate,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ROLES, ActionType.WRITE))],
    service: Annotated[RoleService, Depends(get_role_service)],
):
    await service.update(id, data)

@router.get("/{id}/permissions", response_model=list[RolePermissionResponse], status_code=status.HTTP_200_OK)
async def get_role_permissions(
    id: int,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ROLES, ActionType.READ))],
    service: Annotated[RoleService, Depends(get_role_service)],
) -> list[RolePermissionResponse]:
    return await service.get_permissions(id)

@router.put("/{id}/permissions/{resource}", response_model=RolePermissionResponse, status_code=status.HTTP_200_OK)
async def update_role_permission(
    id: int,
    resource: ResourceType,
    data: RolePermissionUpdate,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ROLES, ActionType.WRITE))],
    service: Annotated[RoleService, Depends(get_role_service)],
) -> RolePermissionResponse:
    return await service.set_permission(id, resource, data)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_role(
    id: int,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ROLES, ActionType.DELETE))],
    service: Annotated[RoleService, Depends(get_role_service)],
):
    await service.delete(id)
