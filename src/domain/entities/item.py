from dataclasses import dataclass
from src.domain.enums import ItemRarity

@dataclass
class ItemEntity:
    id: int
    name: str
    type: str
    rarity: ItemRarity
    source: str
    source_name: str
