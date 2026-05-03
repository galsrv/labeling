from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import is_labels_edit_permitted, is_labels_view_permitted
from core.config import settings as s
from core.dependencies import logging_dependency
from database.config import get_async_session
from frontend.responses import JsonToFrontendResponse
from labels.schemas import LabelTemplatesCreateUpdateSchema, LabelTemplatesPageSchema, LabelTemplatesReadSchema, PrintLabelTestPayload
from labels.service import labels_service
from labels.variables import get_control_codes, get_label_variables

api_labels_router = APIRouter()


@api_labels_router.get(
    '/control_codes',
    response_model=list[str],
    summary='Получить контрольные коды',
    dependencies=[Depends(is_labels_view_permitted), Depends(logging_dependency)],
)
async def get_labels_control_codes() -> list[str]:
    """Эндпоинт получения контрольных кодов для редактора."""
    return get_control_codes()


@api_labels_router.get(
    '/variables',
    response_model=list[str],
    summary='Получить переменные этикетки',
    dependencies=[Depends(is_labels_view_permitted), Depends(logging_dependency)],
)
async def get_labels_variables() -> list[str]:
    """Эндпоинт получения переменных для редактора."""
    return get_label_variables()


@api_labels_router.get(
    '/',
    response_model=LabelTemplatesPageSchema,
    summary='Получить список шаблонов этикетки',
    dependencies=[Depends(is_labels_view_permitted), Depends(logging_dependency)],
)
async def get_labels(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(
        ge=1,
        default=1),
    size: int = Query(
        ge=s.PAGINATION_MIN_SIZE,
        le=s.PAGINATION_MAX_SIZE,
        default=s.PAGINATION_DEFAULT_PAGE_SIZE),
) -> LabelTemplatesPageSchema:
    """Эндпоинт получения списка шаблонов этикеток."""
    labels = await labels_service.get_page(session, page, size)
    return labels


@api_labels_router.get(
    '/{label_id}',
    response_model=LabelTemplatesReadSchema,
    summary='Получить шаблон этикетки',
    dependencies=[Depends(is_labels_view_permitted), Depends(logging_dependency)],
)
async def get_label(
    label_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> LabelTemplatesReadSchema:
    """Эндпоинт получения шаблона этикетки."""
    label = await labels_service.get(session, label_id)
    return label


@api_labels_router.post(
    '/',
    response_model=LabelTemplatesReadSchema,
    summary='Создать шаблон этикетки',
    dependencies=[Depends(is_labels_edit_permitted), Depends(logging_dependency)],
)
async def create_label(
    data_input: LabelTemplatesCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> LabelTemplatesReadSchema:
    """Эндпоинт создания шаблона этикетки."""
    response = await labels_service.create(session, data_input)
    return response


@api_labels_router.put(
    '/{label_id}',
    response_model=LabelTemplatesReadSchema,
    summary='Изменить шаблон этикетки',
    dependencies=[Depends(is_labels_edit_permitted), Depends(logging_dependency)],
)
async def update_label(
    label_id: int,
    data_input: LabelTemplatesCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> LabelTemplatesReadSchema:
    """Эндпоинт изменения шаблона этикетки."""
    response = await labels_service.update(session, label_id, data_input)
    return response


@api_labels_router.delete(
    '/{label_id}',
    summary='Удалить шаблон этикетки',
    dependencies=[Depends(is_labels_edit_permitted), Depends(logging_dependency)],
)
async def delete_label(
    label_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Эндпоинт удаления шаблон этикетки."""
    await labels_service.delete(session, label_id)


@api_labels_router.post(
        '/print_label_test',
        response_model=JsonToFrontendResponse,
        name='web_print_label_test',
        summary='Печать тестовой этикетки',
        dependencies=[Depends(is_labels_view_permitted), Depends(logging_dependency)],
)
async def web_print_label_test(
    label: PrintLabelTestPayload,
    session: AsyncSession = Depends(get_async_session),
) -> JsonToFrontendResponse:
    """Печатаем тестовую этикетку."""
    return await labels_service.print_test_label(session, label)
