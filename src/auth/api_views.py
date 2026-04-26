from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_async_session
from auth.dependencies import get_current_user
from auth.schemas import LoginRequestSchema, TokenPairSchema, RefreshRequestSchema
from auth.service import auth_service
from core.dependencies import logging_dependency
from users.schemas import UserReadSchema

api_auth_router = APIRouter()


@api_auth_router.post(
    '/login',
    response_model=TokenPairSchema,
    summary='Аутентифицировать пользователя',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(logging_dependency)],
)
async def login_user(
    data_input: LoginRequestSchema,
    session: AsyncSession = Depends(get_async_session)
) -> TokenPairSchema:
    """Эндпоинт аутентификации пользователя."""
    response = await auth_service.login(session, data_input)
    return response


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
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(logging_dependency)],
)
async def refresh_tokens(
    data_input: RefreshRequestSchema,
    session: AsyncSession = Depends(get_async_session),
) -> TokenPairSchema:
    """Эндпоинт обновления access/refresh токенов."""
    token_pair = await auth_service.refresh(session, data_input)
    return token_pair
