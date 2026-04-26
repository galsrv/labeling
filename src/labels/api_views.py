from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_async_session
from core.dependencies import logging_dependency
from frontend.responses import JsonToFrontendResponse
from labels.schemas import LabelTemplatesReadSchema, LabelTemplatesCreateUpdateSchema, PrintLabelTestPayload
from labels.service import labels_service
from labels.variables import get_control_codes, get_label_variables

api_labels_router = APIRouter()


@api_labels_router.get(
    '/control_codes',
    response_model=list[str],
    summary='Получить контрольные коды'
)
async def get_labels_control_codes() -> list[str]:
    """Эндпоинт получения контрольных кодов для редактора."""
    return get_control_codes()


@api_labels_router.get(
    '/variables',
    response_model=list[str],
    summary='Получить переменные этикетки'
)
async def get_labels_variables() -> list[str]:
    """Эндпоинт получения переменных для редактора."""
    return get_label_variables()


@api_labels_router.get(
    '/',
    response_model=list[LabelTemplatesReadSchema],
    summary='Получить все шаблоны этикетки'
)
async def get_all_labels(
    session: AsyncSession = Depends(get_async_session)
) -> list[LabelTemplatesReadSchema]:
    """Эндпоинт получения всех шаблонов этикеток."""
    labels = await labels_service.get_all(session)
    return labels


@api_labels_router.get(
    '/{label_id}',
    response_model=LabelTemplatesReadSchema,
    summary='Получить шаблон этикетки'
)
async def get_label(
    label_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> LabelTemplatesReadSchema:
    """Эндпоинт получения шаблона этикетки."""
    label = await labels_service.get(session, label_id)
    return label


@api_labels_router.post(
    '/',
    response_model=LabelTemplatesReadSchema,
    summary='Создать шаблон этикетки'
)
async def create_label(
    data_input: LabelTemplatesCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> LabelTemplatesReadSchema:
    """Эндпоинт создания шаблона этикетки."""
    response = await labels_service.create(session, data_input)
    return response


@api_labels_router.put(
    '/{label_id}',
    response_model=LabelTemplatesReadSchema,
    summary='Изменить шаблон этикетки'
)
async def update_label(
    label_id: int,
    data_input: LabelTemplatesCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> LabelTemplatesReadSchema:
    """Эндпоинт изменения шаблона этикетки."""
    response = await labels_service.update(session, label_id, data_input)
    return response


@api_labels_router.delete(
    '/{label_id}',
    summary='Удалить шаблон этикетки'
)
async def delete_label(
    label_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    """Эндпоинт удаления шаблон этикетки."""
    await labels_service.delete(session, label_id)


@api_labels_router.post(
        '/print_label_test',
        response_model=JsonToFrontendResponse,
        name='web_print_label_test',
        summary='Печать тестовой этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_print_label_test(
    label: PrintLabelTestPayload,
    session: AsyncSession = Depends(get_async_session),
) -> JsonToFrontendResponse:
    """Печатаем тестовую этикетку."""
    return await labels_service.print_test_label(session, label)
