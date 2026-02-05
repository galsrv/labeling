from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates, settings as s
from core.database import get_async_session
from core.dependencies import logging_dependency

from frontend.responses import WebJsonResponse
from scales.service import web_scales_service
from scales.schemas import ScalesShortSchema

web_scales_router = APIRouter()


@web_scales_router.post(
        '/get_weight',
        response_model=WebJsonResponse,
        response_model_exclude_none=True,
        name='web_scales_get_weight',
        summary='Получение веса с весов',
        dependencies=[Depends(logging_dependency)]
)
async def web_scales_get_weight(
    ip: str = Form(),
    port: int = Form(),
    driver_name: str = Form(),
) -> WebJsonResponse:
    """Получаем вес с весов для вывода в интерфейсе."""
    try:
        scales = ScalesShortSchema(ip=ip, port=port, driver_name=driver_name)
    except ValidationError as e:
        return WebJsonResponse(ok=False, message=str(e))

    return await web_scales_service.get_weight(scales)


@web_scales_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список весов',
        name='web_get_all_scales',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_scales(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список весов."""
    all_scales = await web_scales_service.get_all(session)
    return templates.TemplateResponse(
        request=request,
        name='scales.html',
        context={'all_scales': all_scales}
    )


@web_scales_router.get(
        '/create',
        response_class=HTMLResponse,
        name='web_create_scales_form',
        summary='Форма создания весов',
        dependencies=[Depends(logging_dependency)]
)
async def web_create_scales_form(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем форму создания новых весов."""
    context = await web_scales_service.create_form(session)

    return templates.TemplateResponse(
        request=request,
        name='scales_edit.html',
        context=context
    )


@web_scales_router.post(
        '/create',
        name='web_create_scales',
        summary='Создание весов',
        response_model=None,
        dependencies=[Depends(logging_dependency)]
)
async def web_create_scales(
    request: Request,
    ip: str = Form(),
    port: int = Form(),
    driver_id: int = Form(),
    description: str = Form(),
    session: AsyncSession = Depends(get_async_session),
) -> RedirectResponse | HTMLResponse:
    """Создаем весы на основании значений полей формы."""
    scales_id: int | None = await web_scales_service.create(session, ip, port, driver_id, description)

    # При некорректно введенных данных рендерим страницу повторно и выдаем плашку из данных контекста
    if not scales_id:
        context = await web_scales_service.create_form(session)
        context['error_message'] = s.MESSAGE_SAVE_DATA_ERROR
        return templates.TemplateResponse(
            request=request,
            name='scales_edit.html',
            context=context,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(
        url=request.url_for('web_update_scales_form', scales_id=scales_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@web_scales_router.get(
        '/{scales_id}',
        response_class=HTMLResponse,
        name='web_update_scales_form',
        summary='Форма изменения весов',
        dependencies=[Depends(logging_dependency)]
)
async def web_update_scales_form(
    scales_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем форму изменения данных весов."""
    context = await web_scales_service.update_form(session, scales_id)

    return templates.TemplateResponse(
        request=request,
        name='scales_edit.html',
        context=context
    )


@web_scales_router.post(
        '/{scales_id}',
        name='web_update_scales',
        summary='Изменение данных весов',
        response_model=None,
        dependencies=[Depends(logging_dependency)]
)
async def web_update_scales(
    scales_id: int,
    request: Request,
    ip: str = Form(),
    port: int = Form(),
    driver_id: int = Form(),
    description: str = Form(),
    session: AsyncSession = Depends(get_async_session),
) -> RedirectResponse | HTMLResponse:
    """Сохраняем изменения данных весов на основании значений полей формы."""
    updated_scales_id: int | None = await web_scales_service.update(session, scales_id, ip, port, driver_id, description)

    # При некорректно введенных данных рендерим страницу повторно и выдаем плашку из данных контекста
    if not updated_scales_id:
        context = await web_scales_service.update_form(session, scales_id)
        context['error_message'] = s.MESSAGE_SAVE_DATA_ERROR
        return templates.TemplateResponse(
            request=request,
            name='scales_edit.html',
            context=context,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(
        url=request.url_for('web_update_scales_form', scales_id=scales_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@web_scales_router.post(
        '/{scales_id}/delete',
        response_class=HTMLResponse,
        name='web_delete_scales',
        summary='Удаление весов',
        dependencies=[Depends(logging_dependency)]
)
async def web_delete_scales(
    scales_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Удаляем принтер."""
    await web_scales_service.delete(session, scales_id)

    return RedirectResponse(
        url=request.url_for('web_get_all_scales'),
        status_code=status.HTTP_303_SEE_OTHER,
    )
