from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_async_session
from auth.dependencies import is_scales_view_permitted, is_scales_edit_permitted
from core.dependencies import logging_dependency
from core.config import settings as s
from frontend.responses import JsonToFrontendResponse
from scales.schemas import ScalesPageSchema, ScalesReadSchema, ScalesCreateUpdateSchema, ScalesShortSchema
from scales.service import scales_service

api_scales_router = APIRouter()


@api_scales_router.get(
    '/',
    response_model=ScalesPageSchema,
    summary='Получить список весов',
    dependencies=[Depends(is_scales_view_permitted), Depends(logging_dependency)]
)
async def get_scales(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(
        ge=1,
        default=1),
    size: int = Query(
        ge=s.PAGINATION_MIN_SIZE,
        le=s.PAGINATION_MAX_SIZE,
        default=s.PAGINATION_DEFAULT_PAGE_SIZE),
) -> ScalesPageSchema:
    """Эндпоинт получения списка весов."""
    scales = await scales_service.get_page(session, page, size)
    return scales


@api_scales_router.get(
    '/{scales_id}',
    response_model=ScalesReadSchema,
    summary='Получить весы',
    dependencies=[Depends(is_scales_view_permitted), Depends(logging_dependency)]
)
async def get_scales_by_id(
    scales_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> ScalesReadSchema:
    """Эндпоинт получения весов."""
    scales = await scales_service.get(session, scales_id)
    return scales


@api_scales_router.post(
    '/',
    response_model=ScalesReadSchema,
    summary='Создать весы',
    dependencies=[Depends(is_scales_edit_permitted), Depends(logging_dependency)]
)
async def create_scales(
    data_input: ScalesCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> ScalesReadSchema:
    """Эндпоинт создания записи справочника весов."""
    response = await scales_service.create(session, data_input)
    return response


@api_scales_router.put(
    '/{scales_id}',
    response_model=ScalesReadSchema,
    summary='Изменить весы',
    dependencies=[Depends(is_scales_edit_permitted), Depends(logging_dependency)]
)
async def update_scales(
    scales_id: int,
    data_input: ScalesCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> ScalesReadSchema:
    """Эндпоинт изменения записи справочника весов."""
    response = await scales_service.update(session, scales_id, data_input)
    return response


@api_scales_router.delete(
    '/{scales_id}',
    summary='Удалить весы',
    dependencies=[Depends(is_scales_edit_permitted), Depends(logging_dependency)]
)
async def delete_scales(
    scales_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    """Эндпоинт удаления записи справочника весов."""
    await scales_service.delete(session, scales_id)


@api_scales_router.post(
        '/{scales_id}/get_weight',
        response_model=JsonToFrontendResponse,
        response_model_exclude_none=True,
        name='web_scales_get_weight',
        summary='Получить вес с весов',
        dependencies=[Depends(is_scales_view_permitted), Depends(logging_dependency)]
)
async def web_scales_get_weight(
    data_input: ScalesShortSchema,
) -> JsonToFrontendResponse:
    """Получаем вес с весов для вывода в интерфейсе.

    Правильнее было бы делать GET запрос, но пришлось бы отказаться от тела запроса и модель ScalesShortSchema собирать руками
    """
    return await scales_service.get_weight(data_input)
