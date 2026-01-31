from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates
from core.database import get_async_session
from core.dependencies import logging_dependency
from workplaces.service import web_scales_service

web_scales_router = APIRouter()


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
        name='web_create_scale_form',
        summary='Форма создания весов',
        dependencies=[Depends(logging_dependency)]
)
async def web_create_scale_form(
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


@web_scales_router.get(
        '/{scale_id}',
        response_class=HTMLResponse,
        name='web_update_scale_form',
        summary='Форма изменения весов',
        dependencies=[Depends(logging_dependency)]
)
async def web_update_scale_form(
    scale_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем форму изменения данных весов."""
    context = await web_scales_service.get(session, scale_id)

    return templates.TemplateResponse(
        request=request,
        name='scales_edit.html',
        context=context
    )
