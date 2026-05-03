from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, is_users_edit_permitted, is_users_view_permitted
from core.config import settings as s
from core.dependencies import logging_dependency
from database.config import get_async_session
from users.schemas import RoleReadSchema, UserCreateSchema, UserPageSchema, UserReadSchema, UserUpdateSchema
from users.service import roles_service, users_service

api_users_router = APIRouter()


@api_users_router.get(
    '/roles',
    response_model=list[RoleReadSchema],
    summary='Получить все роли',
    dependencies=[Depends(is_users_view_permitted), Depends(logging_dependency)],
)
async def get_all_roles(
    session: AsyncSession = Depends(get_async_session),
) -> list[RoleReadSchema]:
    """Эндпоинт получения всех ролей."""
    roles = await roles_service.get_all(session)
    return roles


@api_users_router.get(
    '/',
    response_model=UserPageSchema,
    summary='Получить список пользователей',
    dependencies=[Depends(is_users_view_permitted), Depends(logging_dependency)],
)
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(
        ge=1,
        default=1),
    size: int = Query(
        ge=s.PAGINATION_MIN_SIZE,
        le=s.PAGINATION_MAX_SIZE,
        default=s.PAGINATION_DEFAULT_PAGE_SIZE),
) -> UserPageSchema:
    """Эндпоинт получения списка пользователей."""
    users = await users_service.get_page(session, page, size)
    return users


@api_users_router.get(
    '/{user_id}',
    response_model=UserReadSchema,
    summary='Получить пользователя',
    dependencies=[Depends(is_users_view_permitted), Depends(logging_dependency)],
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema:
    """Эндпоинт получения пользователя."""
    user = await users_service.get(session, user_id)
    return user


@api_users_router.post(
    '/',
    response_model=UserReadSchema,
    summary='Создать пользователя',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(is_users_edit_permitted), Depends(logging_dependency)],
)
async def create_user(
    data_input: UserCreateSchema,
    current_user: UserReadSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema:
    """Эндпоинт создания пользователя."""
    response = await users_service.create(session, data_input, current_user)
    return response


@api_users_router.put(
    '/{user_id}',
    response_model=UserReadSchema,
    summary='Изменить пользователя',
    dependencies=[Depends(is_users_edit_permitted), Depends(logging_dependency)],
)
async def update_user(
    user_id: int,
    data_input: UserUpdateSchema,
    current_user: UserReadSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema:
    """Эндпоинт изменения пользователя."""
    response = await users_service.update(session, user_id, data_input, current_user)
    return response
