from src.domain.entities.role import RoleEntity
from src.domain.enums import ActionType, ResourceType
from src.domain.exceptions import NotFoundException
from src.domain.repositories.role import RoleRepository
from src.schemas.role import RolePermissionResponse, RolePermissionUpdate, RoleUpdate

class RoleService:
    def __init__(self, role_repo: RoleRepository):
        self._role_repo = role_repo

    async def get_all(self) -> list[RoleEntity]:
        return await self._role_repo.get_all()

    async def get_by_id(self, id: int) -> RoleEntity:
        role = await self._role_repo.get_by_id(id)
        if not role:
            raise NotFoundException("Role not found")
        return role

    async def create(self, name: str) -> RoleEntity:
        return await self._role_repo.create(name)

    async def update(self, id: int, data: RoleUpdate):
        await self._role_repo.update(id, data.name)

    async def delete(self, id: int):
        await self._role_repo.delete(id)

    async def check_permission(
        self,
        role_id: int,
        resource: ResourceType,
        action: ActionType,
    ) -> bool:
        return await self._role_repo.check_permission(
            role_id,
            resource,
            action
        )

    async def get_permissions(self, role_id: int) -> list[RolePermissionResponse]:
        role = await self._role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role not found")

        permissions = await self._role_repo.get_permissions(role_id)
        return [
            RolePermissionResponse(
                resource=resource,
                can_read=can_read,
                can_write=can_write,
                can_delete=can_delete,
            )
            for resource, can_read, can_write, can_delete in permissions
        ]

    async def set_permission(
        self,
        role_id: int,
        resource: ResourceType,
        data: RolePermissionUpdate,
    ) -> RolePermissionResponse:
        role = await self._role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role not found")

        resource, can_read, can_write, can_delete = await self._role_repo.set_permission(
            role_id=role_id,
            resource=resource,
            can_read=data.can_read,
            can_write=data.can_write,
            can_delete=data.can_delete,
        )
        return RolePermissionResponse(
            resource=resource,
            can_read=can_read,
            can_write=can_write,
            can_delete=can_delete,
        )