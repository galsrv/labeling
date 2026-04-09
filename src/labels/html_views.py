from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_labels_router = APIRouter()


@html_labels_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список шаблонов этикеток',
        name='web_get_all_labels',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_labels(
    request: Request,
) -> HTMLResponse:
    """Отображаем список шаблонов этикеток."""
    return templates.TemplateResponse(
        request=request,
        name='labels.html',
    )


@html_labels_router.get(
        '/create',
        response_class=HTMLResponse,
        name='web_create_label_form',
        summary='Создание шаблона этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_create_label_form(
    request: Request,
) -> HTMLResponse:
    """Создаем шаблон этикетки."""
    return templates.TemplateResponse(
        request=request,
        name='label_edit.html',
        context={'mode': 'create'}
    )


@html_labels_router.get(
        '/{label_id}',
        response_class=HTMLResponse,
        name='web_update_label_form',
        summary='Шаблон этикетки',
        dependencies=[Depends(logging_dependency)]
)
async def web_update_label_form(
    label_id: int,
    request: Request,
) -> HTMLResponse:
    """Отображаем шаблон этикетки."""
    return templates.TemplateResponse(
        request=request,
        name='label_edit.html',
        context={'mode': 'update'}
    )
