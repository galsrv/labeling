import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.exceptions import InvalidCredentialsError, NotAuthorizedError
from auth.tokens import tokens
from core.config import settings as s
from database.config import get_async_session
from database.exceptions import ObjectNotFoundError
from users.schemas import UserReadSchema
from users.service import users_service


def _extract_access_token(request: Request) -> str:
    header = request.headers.get('authorization')
    if header and header.lower().startswith('bearer '):
        return header.split(' ', 1)[1].strip()

    cookie_token = request.cookies.get('access_token')
    if cookie_token:
        return cookie_token

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, s.MESSAGE_ACCESS_TOKEN_IS_MISSING)


async def get_current_user(request: Request, session: AsyncSession = Depends(get_async_session)) -> UserReadSchema:
    """Зависимость, подставляющая текущего пользователя."""
    raw_token = _extract_access_token(request)

    try:
        payload = tokens.decode_token(raw_token)
    except InvalidCredentialsError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, s.MESSAGE_ACCESS_TOKEN_IS_EXPIRED)
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, s.MESSAGE_WRONG_ACCESS_TOKEN)

    try:
        user_id = int(payload['sub'])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, s.MESSAGE_WRONG_ACCESS_TOKEN)

    try:
        user: UserReadSchema = await users_service.get(session, user_id)
    except ObjectNotFoundError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))

    if not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, s.MESSAGE_AUTHENTICATION_FAILED)

    return user


async def get_current_user_optional(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema | None:
    """Возвзращвем текущем пользователя или None."""
    try:
        return await get_current_user(request, session)
    except HTTPException:
        return None


def is_items_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_items_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_items_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_items_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_labels_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_labels_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_labels_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_labels_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_orders_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_orders_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_orders_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_orders_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_printers_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_printers_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_printers_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_printers_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_scales_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_scales_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_scales_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_scales_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_sgtins_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_sgtins_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_sgtins_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_sgtins_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_users_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_users_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_users_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_users_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_workplaces_view_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_workplaces_view_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)


def is_workplaces_edit_permitted(request: Request, current_user: UserReadSchema = Depends(get_current_user)) -> None:
    """Проверка полномочия."""
    if not current_user.role.is_workplaces_edit_permitted:
        raise NotAuthorizedError(s.MESSAGE_USER_NOT_AUTHORIZED)
