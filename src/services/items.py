from src.domain.entities.item import ItemEntity
from src.domain.exceptions import NotFoundException
from src.domain.repositories.item import ItemRepository
from src.schemas.item import ItemCreate, ItemFilter, ItemUpdate

class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self._item_repo = item_repo

    async def get_all(self, filters: ItemFilter) -> list[ItemEntity]:
        return await self._item_repo.get_page(filters)

    async def get_by_id(self, id: int) -> ItemEntity:
        item = await self._item_repo.get_by_id(id)
        if not item:
            raise NotFoundException("Item not found")
        return item

    async def count(self) -> int:
        return await self._item_repo.count()

    async def create(self, data: ItemCreate) -> ItemEntity:
        return await self._item_repo.create(data)

    async def update(self, id: int, data: ItemUpdate):
        await self._item_repo.update(id, data)

    async def delete(self, id: int):
        await self._item_repo.delete(id)