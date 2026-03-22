from pydantic import BaseModel, Field

from src.domain.enums import ItemRarity

class ItemCreate(BaseModel):
    name: str
    type: str
    rarity: ItemRarity
    source: str
    source_name: str

class ItemUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    rarity: ItemRarity | None = None
    source: str | None = None
    source_name: str | None = None

class ItemFilter(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=10, le=100, default=50)
    search: str | None = None
    rarity: ItemRarity | None = None

class ItemResponse(BaseModel):
    id: int
    name: str
    type: str
    rarity: ItemRarity
    source: str
    source_name: str
