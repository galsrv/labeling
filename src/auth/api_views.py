from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_async_session
from core.config import settings as s
from auth.dependencies import get_current_user
from auth.schemas import LoginRequestSchema, RefreshRequestSchema, TokenPairSchema
from auth.service import auth_service
from core.dependencies import logging_dependency
from users.schemas import UserReadSchema

api_auth_router = APIRouter()


def set_tokens_cookies_helper(response: Response, token_pair: TokenPairSchema) -> Response:
    """Установка кук в структуру ответа."""
    response.set_cookie(
        key='access_token',
        value=token_pair.access_token,
        httponly=True,
        secure=s.PROD_ENVIRONMENT,
        samesite='lax',
        path='/',
    )
    response.set_cookie(
        key='refresh_token',
        value=token_pair.refresh_token,
        httponly=True,
        secure=s.PROD_ENVIRONMENT,
        samesite='lax',
        path='/',
    )
    return response


@api_auth_router.post(
    '/login',
    summary='Аутентифицировать пользователя',
    response_model=TokenPairSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(logging_dependency)],
)
async def login_user(
    data_input: LoginRequestSchema,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
) -> TokenPairSchema:
    """Эндпоинт аутентификации пользователя."""
    token_pair = await auth_service.login(session, data_input)
    set_tokens_cookies_helper(response, token_pair)
    return token_pair


@api_auth_router.post(
    '/logout',
    summary='Разлогинить пользователя',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(logging_dependency)],
)
async def logout_user(
    response: Response,
    data_input: RefreshRequestSchema | None = None,
    refresh_token_from_cookie: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    """Эндпоинт выхода из учетной записи пользователя."""
    refresh_token = (data_input.refresh_token if data_input else None) or refresh_token_from_cookie

    if refresh_token is not None:
        await auth_service.logout(session, refresh_token)

    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')

    return


@api_auth_router.get(
    '/me',
    summary='Получить профиль текущего пользователя',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(logging_dependency)],
)
async def me(
    user: UserReadSchema = Depends(get_current_user),
) -> UserReadSchema:
    """Эндпоинт получения профиля текущего пользователя по access-токену JWT."""
    return user


@api_auth_router.post(
    '/tokens_refresh',
    summary='Обновить access/refresh токены',
    response_model=TokenPairSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(logging_dependency)],
)
async def refresh_tokens(
    response: Response,
    data_input: RefreshRequestSchema | None = None,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_async_session),
) -> TokenPairSchema:
    """Эндпоинт обновления access/refresh токенов.

    Универсальный эндпоинт:
    - Браузер присылает токен из кук
    - Внешняя система шлет токен в теле запроса
    Отдаем в любом случае новую пару токенов.

    За универсальность надо платить - HttpOnly имеет мало смысла, JS имеет доступ к телу ответа.
    """
    refresh_token = (data_input.refresh_token if data_input else None) or refresh_token

    if refresh_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    data_input = RefreshRequestSchema(refresh_token=refresh_token)
    token_pair = await auth_service.refresh(session, data_input)
    set_tokens_cookies_helper(response, token_pair)
    return token_pair
