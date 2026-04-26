from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_async_session
from core.dependencies import logging_dependency
from frontend.responses import JsonToFrontendResponse
from scales.schemas import ScalesReadSchema, ScalesCreateUpdateSchema, ScalesShortSchema
from scales.service import scales_service

api_scales_router = APIRouter()


@api_scales_router.get(
    '/',
    response_model=list[ScalesReadSchema],
    summary='Получить все весы'
)
async def get_all_scales(
    session: AsyncSession = Depends(get_async_session)
) -> list[ScalesReadSchema]:
    """Эндпоинт получения всех весов."""
    scales = await scales_service.get_all(session)
    return scales


@api_scales_router.get(
    '/{scales_id}',
    response_model=ScalesReadSchema,
    summary='Получить весы'
)
async def get_scales(
    scales_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> ScalesReadSchema:
    """Эндпоинт получения весов."""
    scales = await scales_service.get(session, scales_id)
    return scales


@api_scales_router.post(
    '/',
    response_model=ScalesReadSchema,
    summary='Создать весы'
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
    summary='Изменить весы'
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
    summary='Удалить весы'
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
        dependencies=[Depends(logging_dependency)]
)
async def web_scales_get_weight(
    data_input: ScalesShortSchema,
) -> JsonToFrontendResponse:
    """Получаем вес с весов для вывода в интерфейсе.

    Правильнее было бы делать GET запрос, но пришлось бы отказаться от тела запроса и модель ScalesShortSchema собирать руками
    """
    return await scales_service.get_weight(data_input)
