from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from items.schemas import ItemReadSchema
from items.service import api_items_service

api_items_router = APIRouter()


@api_items_router.get(
    '/', response_model=list[ItemReadSchema], summary='Получить все продукты')
async def get_items(
    session: AsyncSession = Depends(get_async_session)
) -> list[ItemReadSchema]:
    """Эндпоинт получения всех продуктов."""
    items = await api_items_service.get_all(session)
    return items


@api_items_router.get(
    '/{item_id}', response_model=ItemReadSchema, summary='Получить продукт')
async def get_item(
    item_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> ItemReadSchema:
    """Эндпоинт получения продукта."""
    item = await api_items_service.get(session, item_id)
    return item
