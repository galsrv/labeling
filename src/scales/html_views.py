from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_scales_router = APIRouter()


@html_scales_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список весов',
        name='web_get_all_scales',
        dependencies=[Depends(logging_dependency)],
)
async def web_get_all_scales(
    request: Request,
) -> HTMLResponse:
    """Отображаем список весов."""
    return templates.TemplateResponse(
        request=request,
        name='scales.html',
    )


@html_scales_router.get(
        '/create',
        response_class=HTMLResponse,
        name='web_create_scales_form',
        summary='Форма создания весов',
        dependencies=[Depends(logging_dependency)],
)
async def web_create_scales_form(
    request: Request,
) -> HTMLResponse:
    """Отображаем форму создания новых весов."""
    return templates.TemplateResponse(
        request=request,
        name='scales_edit.html',
        context={'mode': 'create'},
    )


@html_scales_router.get(
        '/{scales_id}',
        response_class=HTMLResponse,
        name='web_update_scales_form',
        summary='Форма изменения весов',
        dependencies=[Depends(logging_dependency)],
)
async def web_update_scales_form(
    request: Request,
    scales_id: int,
) -> HTMLResponse:
    """Отображаем форму изменения весов."""
    return templates.TemplateResponse(
        request=request,
        name='scales_edit.html',
        context={'mode': 'update'},
    )
