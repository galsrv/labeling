from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import is_items_view_permitted
from core.config import settings as s
from core.dependencies import logging_dependency
from database.config import get_async_session
from items.schemas import ItemReadSchema, ItemsPageSchema
from items.service import items_service

api_items_router = APIRouter()


@api_items_router.get(
    '/',
    response_model=ItemsPageSchema,
    summary='Получить список продуктов',
    dependencies=[Depends(is_items_view_permitted), Depends(logging_dependency)],
)
async def get_items(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(
        ge=1,
        default=1),
    size: int = Query(
        ge=s.PAGINATION_MIN_SIZE,
        le=s.PAGINATION_MAX_SIZE,
        default=s.PAGINATION_DEFAULT_PAGE_SIZE),
) -> ItemsPageSchema:
    """Эндпоинт получения списка продуктов."""
    items = await items_service.get_page(session, page, size)
    return items


@api_items_router.get(
    '/{item_id}',
    response_model=ItemReadSchema,
    summary='Получить продукт',
    dependencies=[Depends(is_items_view_permitted), Depends(logging_dependency)],
)
async def get_item(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> ItemReadSchema:
    """Эндпоинт получения продукта."""
    item = await items_service.get(session, item_id)
    return item
