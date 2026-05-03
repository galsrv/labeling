from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_printers_router = APIRouter()


@html_printers_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список принтеров',
        name='web_get_all_printers',
        dependencies=[Depends(logging_dependency)],
)
async def web_get_all_printers(
    request: Request,
) -> HTMLResponse:
    """Отображаем список принтеров."""
    return templates.TemplateResponse(
        request=request,
        name='printers.html',
    )


@html_printers_router.get(
        '/create',
        response_class=HTMLResponse,
        name='web_create_printer_form',
        summary='Форма создания принтера',
        dependencies=[Depends(logging_dependency)],
)
async def web_create_printer_form(
    request: Request,
) -> HTMLResponse:
    """Отображаем форму создания нового принтера."""
    return templates.TemplateResponse(
        request=request,
        name='printer_edit.html',
        context={'mode': 'create'},
    )


@html_printers_router.get(
        '/{printer_id}',
        response_class=HTMLResponse,
        name='web_update_printer_form',
        summary='Форма изменения принтера',
        dependencies=[Depends(logging_dependency)],
)
async def web_update_printer_form(
    request: Request,
    printer_id: int,
) -> HTMLResponse:
    """Отображаем форму изменения данных принтера."""
    return templates.TemplateResponse(
        request=request,
        name='printer_edit.html',
        context={'mode': 'update'},
    )
