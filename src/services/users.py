from src.domain.entities.user import UserEntity
from src.domain.exceptions import NotFoundException
from src.domain.repositories.user import UserRepository
from src.schemas.user import UserCreate, UserFilter, UserUpdate

class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def get_all(self, filters: UserFilter) -> list[UserEntity]:
        return await self._user_repo.get_page(filters)

    async def get_by_id(self, id: int) -> UserEntity:
        user = await self._user_repo.get_by_id(id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def create(self, data: UserCreate) -> UserEntity:
        return await self._user_repo.create(data)

    async def update(self, id: int, data: UserUpdate):
        await self._user_repo.update(id, data)

    async def delete(self, id: int):
        await self._user_repo.delete(id)

    async def soft_delete(self, id: int):
        await self._user_repo.soft_delete(id)