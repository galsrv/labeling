from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_async_session
from core.dependencies import logging_dependency
from users.schemas import UserReadSchema, UserCreateSchema, UserUpdateSchema, RoleReadSchema
from users.service import users_service, roles_service

api_users_router = APIRouter()


@api_users_router.get(
    '/roles',
    response_model=list[RoleReadSchema],
    summary='Получить все роли',
    dependencies=[Depends(logging_dependency)],
)
async def get_all_roles(
    session: AsyncSession = Depends(get_async_session)
) -> list[UserReadSchema]:
    """Эндпоинт получения всех ролей."""
    roles = await roles_service.get_all(session)
    return roles


@api_users_router.get(
    '/',
    response_model=list[UserReadSchema],
    summary='Получить всех пользователей',
    dependencies=[Depends(logging_dependency)],
)
async def get_all_users(
    session: AsyncSession = Depends(get_async_session)
) -> list[UserReadSchema]:
    """Эндпоинт получения всех пользователей."""
    users = await users_service.get_all(session)
    return users


@api_users_router.get(
    '/{user_id}',
    response_model=UserReadSchema,
    summary='Получить пользователя',
    dependencies=[Depends(logging_dependency)],
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    """Эндпоинт получения пользователя."""
    user = await users_service.get(session, user_id)
    return user


@api_users_router.post(
    '/',
    response_model=UserReadSchema,
    summary='Создать пользователя',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(logging_dependency)],
)
async def create_user(
    data_input: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    """Эндпоинт создания пользователя."""
    response = await users_service.create(session, data_input)
    return response


@api_users_router.put(
    '/{user_id}',
    response_model=UserReadSchema,
    summary='Изменить пользователя',
    dependencies=[Depends(logging_dependency)],
)
async def update_user(
    user_id: int,
    data_input: UserUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    """Эндпоинт изменения пользователя."""
    response = await users_service.update(session, user_id, data_input)
    return response
