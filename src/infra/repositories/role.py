from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.role import RoleEntity
from src.domain.enums import ActionType, ResourceType
from src.domain.repositories.role import RoleRepository
from src.infra.models import Role, RolePermission

class SqlRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: Role) -> RoleEntity:
        return RoleEntity(
            id=model.id,
            name=model.name,
        )

    async def get_by_id(self, id: int) -> RoleEntity | None:
        result = await self._session.execute(select(Role).where(Role.id == id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[RoleEntity]:
        result = await self._session.execute(select(Role))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def create(self, name: str) -> RoleEntity:
        model = Role(name=name)
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, id: int, name: str):
        await self._session.execute(
            update(Role)
            .where(Role.id == id)
            .values(name=name)
        )

    async def delete(self, id: int):
        await self._session.execute(delete(Role).where(Role.id == id))

    async def check_permission(
        self,
        role_id: int,
        resource: ResourceType,
        action: ActionType
    ):
        result = await self._session.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.resource == resource,
            )
        )
        perm = result.scalar_one_or_none()

        if not perm:
            return False
        
        match action:
            case ActionType.READ:
                return perm.can_read
            case ActionType.WRITE:
                return perm.can_write
            case ActionType.DELETE:
                return perm.can_delete

    async def get_permissions(self, role_id: int) -> list[tuple[ResourceType, bool, bool, bool]]:
        result = await self._session.execute(
            select(RolePermission).where(RolePermission.role_id == role_id)
        )
        perms = result.scalars().all()
        return [
            (perm.resource, perm.can_read, perm.can_write, perm.can_delete)
            for perm in perms
        ]

    async def set_permission(
        self,
        role_id: int,
        resource: ResourceType,
        can_read: bool,
        can_write: bool,
        can_delete: bool,
    ) -> tuple[ResourceType, bool, bool, bool]:
        result = await self._session.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.resource == resource,
            )
        )
        perm = result.scalar_one_or_none()

        if perm is None:
            perm = RolePermission(
                role_id=role_id,
                resource=resource,
                can_read=can_read,
                can_write=can_write,
                can_delete=can_delete,
            )
            self._session.add(perm)
            await self._session.flush()
            return (perm.resource, perm.can_read, perm.can_write, perm.can_delete)

        perm.can_read = can_read
        perm.can_write = can_write
        perm.can_delete = can_delete
        await self._session.flush()
        return (perm.resource, perm.can_read, perm.can_write, perm.can_delete)