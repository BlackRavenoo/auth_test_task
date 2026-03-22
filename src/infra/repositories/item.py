from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.item import ItemEntity
from src.domain.repositories.item import ItemRepository
from src.infra.models import Item
from src.schemas.item import ItemCreate, ItemFilter, ItemUpdate

class SqlItemRepository(ItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: Item) -> ItemEntity:
        from src.domain.enums import ItemRarity

        return ItemEntity(
            id=model.id,
            name=model.name,
            type=model.type,
            rarity=ItemRarity(model.rarity.value),
            source=model.source,
            source_name=model.source_name,
        )

    async def get_by_id(self, id: int) -> ItemEntity | None:
        result = await self._session.execute(select(Item).where(Item.id == id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_page(self, filters: ItemFilter) -> list[ItemEntity]:
        query = select(Item)

        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.where(Item.name.ilike(search_pattern))

        if filters.rarity:
            query = query.where(Item.rarity == filters.rarity)

        query = query.offset((filters.page - 1) * filters.page_size)\
            .limit(filters.page_size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Item))
        return result.scalar()

    async def create(self, data: ItemCreate) -> ItemEntity:
        model = Item(
            name=data.name,
            type=data.type,
            rarity=data.rarity,
            source=data.source,
            source_name=data.source_name,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, id: int, data: ItemUpdate):
        values = data.model_dump(exclude_none=True)

        if not values:
            return

        await self._session.execute(
            update(Item)
            .where(Item.id == id)
            .values(**values)
        )

    async def delete(self, id: int):
        await self._session.execute(delete(Item).where(Item.id == id))