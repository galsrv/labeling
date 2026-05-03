from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import is_workplaces_view_permitted
from core.config import settings as s
from core.dependencies import logging_dependency
from database.config import get_async_session
from workplaces.schemas import WorkplacePageSchema, WorkplaceReadSchema
from workplaces.service import workplaces_service

api_workplaces_router = APIRouter()


@api_workplaces_router.get(
    '/',
    response_model=WorkplacePageSchema,
    summary='Получить список рабочих мест',
    dependencies=[Depends(is_workplaces_view_permitted), Depends(logging_dependency)],
)
async def get_workplaces(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(
        ge=1,
        default=1),
    size: int = Query(
        ge=s.PAGINATION_MIN_SIZE,
        le=s.PAGINATION_MAX_SIZE,
        default=s.PAGINATION_DEFAULT_PAGE_SIZE),
) -> WorkplacePageSchema:
    """Эндпоинт получения списка рабочих мест."""
    workplaces = await workplaces_service.get_page(session, page, size)
    return workplaces


@api_workplaces_router.get(
    '/{workplace_id}',
    response_model=WorkplaceReadSchema,
    summary='Получить рабочее место',
    dependencies=[Depends(is_workplaces_view_permitted), Depends(logging_dependency)],
)
async def get_workplace(
    workplace_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> WorkplaceReadSchema:
    """Эндпоинт получения рабочего места."""
    workplace = await workplaces_service.get(session, workplace_id)
    return workplace
