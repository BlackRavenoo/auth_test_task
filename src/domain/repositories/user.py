from abc import ABC, abstractmethod
from src.domain.entities.user import UserEntity
from src.schemas.user import UserCreate, UserFilter, UserUpdate

class UserRepository(ABC):
    @abstractmethod
    async def create(self, schema: UserCreate) -> UserEntity:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> UserEntity | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        pass

    @abstractmethod
    async def get_page(self, filters: UserFilter) -> list[UserEntity]:
        pass

    @abstractmethod
    async def update(self, id: int, schema: UserUpdate):
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass

    @abstractmethod
    async def soft_delete(self, id: int):
        pass