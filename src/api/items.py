from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import ItemServiceDep, require_permission
from src.domain.entities.item import ItemEntity
from src.domain.entities.user import UserEntity
from src.domain.enums import ActionType, ItemRarity, ResourceType
from src.schemas.item import ItemCreate, ItemFilter, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=list[ItemResponse], status_code=status.HTTP_200_OK)
async def get_items(
    service: ItemServiceDep,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ITEMS, ActionType.READ))],
    search: str | None = None,
    rarity: ItemRarity | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=10, le=100),
) -> list[ItemEntity]:
    filters = ItemFilter(
        search=search,
        rarity=rarity,
        page=page,
        page_size=page_size,
    )
    return await service.get_all(filters)

@router.get("/count", status_code=status.HTTP_200_OK)
async def get_items_count(
    service: ItemServiceDep,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ITEMS, ActionType.READ))],
) -> int:
    return await service.count()

@router.get("/{id:int}", response_model=ItemResponse, status_code=status.HTTP_200_OK)
async def get_item(
    service: ItemServiceDep,
    id: int,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ITEMS, ActionType.READ))],
) -> ItemEntity:
    return await service.get_by_id(id)

@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    service: ItemServiceDep,
    data: ItemCreate,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ITEMS, ActionType.WRITE))],
) -> ItemEntity:
    return await service.create(data)

@router.patch("/{id:int}", status_code=status.HTTP_200_OK)
async def update_item(
    service: ItemServiceDep,
    id: int,
    data: ItemUpdate,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ITEMS, ActionType.WRITE))],
):
    await service.update(id, data)

@router.delete("/{id:int}", status_code=status.HTTP_200_OK)
async def delete_item(
    id: int,
    _user: Annotated[UserEntity, Depends(require_permission(ResourceType.ITEMS, ActionType.DELETE))],
    service: ItemServiceDep,
):
    await service.delete(id)
