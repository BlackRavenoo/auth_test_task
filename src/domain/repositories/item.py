from abc import ABC, abstractmethod
from src.domain.entities.item import ItemEntity
from src.schemas.item import ItemCreate, ItemUpdate, ItemFilter

class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> ItemEntity | None:
        pass

    @abstractmethod
    async def get_page(self, filters: ItemFilter) -> list[ItemEntity]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def create(self, data: ItemCreate) -> ItemEntity:
        pass

    @abstractmethod
    async def update(self, id: int, data: ItemUpdate):
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass
