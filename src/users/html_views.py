from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_users_router = APIRouter()


@html_users_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список пользователей',
        name='web_get_all_users',
        dependencies=[Depends(logging_dependency)],
)
async def web_get_all_users(
    request: Request,
) -> HTMLResponse:
    """Отображаем список пользователей."""
    return templates.TemplateResponse(
        request=request,
        name='users.html',
    )


@html_users_router.get(
        '/create',
        response_class=HTMLResponse,
        name='web_create_user_form',
        summary='Форма создания пользователя',
        dependencies=[Depends(logging_dependency)],
)
async def web_create_user_form(
    request: Request,
) -> HTMLResponse:
    """Отображаем форму создания нового пользователя."""
    return templates.TemplateResponse(
        request=request,
        name='user_edit.html',
        context={'mode': 'create'},
    )


@html_users_router.get(
        '/{user_id}',
        response_class=HTMLResponse,
        name='web_update_user_form',
        summary='Форма изменения пользователя',
        dependencies=[Depends(logging_dependency)],
)
async def web_update_user_form(
    request: Request,
    user_id: int,
) -> HTMLResponse:
    """Отображаем форму изменения данных пользователя."""
    return templates.TemplateResponse(
        request=request,
        name='user_edit.html',
        context={'mode': 'update'},
    )
