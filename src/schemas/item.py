from pydantic import BaseModel, Field

from src.domain.enums import ItemRarity

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    type: str = Field(min_length=1, max_length=32)
    rarity: ItemRarity
    source: str = Field(min_length=1, max_length=16)
    source_name: str = Field(min_length=1, max_length=64)

class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    type: str | None = Field(default=None, min_length=1, max_length=32)
    rarity: ItemRarity | None = None
    source: str | None = Field(default=None, min_length=1, max_length=16)
    source_name: str | None = Field(default=None, min_length=1, max_length=64)

class ItemFilter(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=10, le=100, default=50)
    search: str | None = Field(default=None, min_length=1, max_length=256)
    rarity: ItemRarity | None = None

class ItemResponse(BaseModel):
    id: int
    name: str
    type: str
    rarity: ItemRarity
    source: str
    source_name: str
