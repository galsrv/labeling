from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from auth.dependencies import get_current_user_optional
from core.config import templates
from core.dependencies import logging_dependency
from users.schemas import UserReadSchema

html_auth_router = APIRouter()


@html_auth_router.get(
        '/login',
        response_class=HTMLResponse,
        summary='Аутентификация пользователя',
        name='web_user_login',
        dependencies=[Depends(logging_dependency)],
)
async def web_user_login(
    request: Request,
    current_user: UserReadSchema = Depends(get_current_user_optional),
) -> HTMLResponse:
    """Аутентификация пользователя."""
    if current_user is not None:
        return RedirectResponse(
            url=request.url_for('site_root'),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name='login.html',
    )


@html_auth_router.get(
        '/me',
        response_class=HTMLResponse,
        summary='Профайл пользователя',
        name='web_user_profile',
        dependencies=[Depends(logging_dependency)],
)
async def web_user_profile(
    request: Request,
) -> HTMLResponse:
    """Профайл пользователя."""
    return templates.TemplateResponse(
        request=request,
        name='me.html',
    )
