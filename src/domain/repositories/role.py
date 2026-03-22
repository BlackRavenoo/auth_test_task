from abc import ABC, abstractmethod
from src.domain.entities.role import RoleEntity
from src.domain.enums import ActionType, ResourceType

class RoleRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> RoleEntity | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[RoleEntity]:
        pass

    @abstractmethod
    async def create(self, name: str) -> RoleEntity:
        pass

    @abstractmethod
    async def update(self, id: int, name: str):
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass

    @abstractmethod
    async def check_permission(
        self,
        role_id: int,
        resource: ResourceType,
        action: ActionType
    ) -> bool:
        pass

    @abstractmethod
    async def get_permissions(self, role_id: int) -> list[tuple[ResourceType, bool, bool, bool]]:
        pass

    @abstractmethod
    async def set_permission(
        self,
        role_id: int,
        resource: ResourceType,
        can_read: bool,
        can_write: bool,
        can_delete: bool,
    ) -> tuple[ResourceType, bool, bool, bool]:
        pass