from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates
from core.database import get_async_session
from core.dependencies import logging_dependency
from labels.schemas import PrintLabelTestPayload
from labels.service import web_labels_service

web_labels_router = APIRouter()


@web_labels_router.post(
        '/print_label_test',
        response_class=JSONResponse,
        name='web_print_label_test',
        summary='Печать тестовой этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_print_label_test(
    payload: PrintLabelTestPayload,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """Печатаем тестовую этикетку."""
    return await web_labels_service.print_test_label(session, payload)


@web_labels_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список шаблонов этикеток',
        name='web_get_all_labels',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_labels(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список шаблонов этикеток."""
    all_labels = await web_labels_service.get_all(session)
    return templates.TemplateResponse(
        request=request,
        name='labels.html',
        context={'all_labels': all_labels}
    )


@web_labels_router.get(
        '/create',
        response_class=HTMLResponse,
        name='web_create_label_form',
        summary='Создание шаблона этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_create_label_form(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Создаем шаблон этикетки."""
    context = await web_labels_service.create_form(session)

    return templates.TemplateResponse(
        request=request,
        name='label_edit.html',
        context=context
    )


@web_labels_router.get(
        '/{label_id}',
        response_class=HTMLResponse,
        name='web_update_label_form',
        summary='Шаблон этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_update_label_form(
    label_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем шаблон этикетки."""
    context = await web_labels_service.get(session, label_id)

    return templates.TemplateResponse(
        request=request,
        name='label_edit.html',
        context=context
    )


@web_labels_router.post(
        '/create',
        response_class=HTMLResponse,
        name='web_create_label',
        summary='Создание шаблона этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_create_label(
    request: Request,
    name: str = Form(),
    driver_id: int = Form(),
    print_command: str = Form(),
    # Можно переделать три поля на data: LabelTemplatesCreateUpdateWebSchema = Form()
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Сохраняем изменения шаблона этикетки."""
    label_id = await web_labels_service.create(session, name, driver_id, print_command)

    return RedirectResponse(
        url=request.url_for('web_update_label_form', label_id=label_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@web_labels_router.post(
        '/{label_id}/delete',
        response_class=HTMLResponse,
        name='web_delete_label',
        summary='Удаление шаблона этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_delete_label(
    label_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Удаляем шаблон этикетки."""
    await web_labels_service.delete(session, label_id)

    return RedirectResponse(
        url=request.url_for('web_get_all_labels'),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@web_labels_router.post(
        '/{label_id}',
        response_class=HTMLResponse,
        name='web_update_label',
        summary='Редактирование шаблона этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_update_label(
    label_id: int,
    request: Request,
    name: str = Form(),
    driver_id: int = Form(),
    print_command: str = Form(),
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Сохраняем изменения шаблона этикетки."""
    await web_labels_service.update(session, label_id, name, driver_id, print_command)

    return RedirectResponse(
        url=request.url_for('web_update_label_form', label_id=label_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
