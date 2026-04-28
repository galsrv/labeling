from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_auth_router = APIRouter()


@html_auth_router.get(
        '/login',
        response_class=HTMLResponse,
        summary='Аутентификация пользователя',
        name='web_user_login',
        dependencies=[Depends(logging_dependency)]
)
async def web_user_login(
    request: Request,
) -> HTMLResponse:
    """Аутентификация пользователя."""
    return templates.TemplateResponse(
        request=request,
        name='login.html',
    )


@html_auth_router.get(
        '/me',
        response_class=HTMLResponse,
        summary='Профайл пользователя',
        name='web_user_profile',
        dependencies=[Depends(logging_dependency)]
)
async def web_user_profile(
    request: Request,
) -> HTMLResponse:
    """Профайл пользователя."""
    return templates.TemplateResponse(
        request=request,
        name='me.html',
    )
