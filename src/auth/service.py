from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from auth.exceptions import (
    InvalidCredentialsError,
    RefreshTokenCreationError,
    RefreshTokenDeletionError,
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
)
from auth.repository import tokens_repo
from auth.schemas import LoginRequestSchema, RefreshRequestSchema, RefreshTokenCreateSchema, RefreshTokenReadSchema, TokenPairSchema
from auth.tokens import tokens
from core.config import settings as s
from database.exceptions import ObjectNotFoundError, ObjectNotModifiedError
from users.schemas import UserReadSchema, UserWithHashReadSchema
from users.service import users_service


class AuthService():
    """Класс сервисных методов модуля аутентификации."""

    async def _get_user_or_raise(self, session: AsyncSession, data_input: LoginRequestSchema) -> UserReadSchema:
        """Проверка введенной пары юзернейм-пароль."""
        try:
            user: UserWithHashReadSchema = await users_service.get_by_username(session, data_input.username)
        except ObjectNotFoundError:
            raise InvalidCredentialsError(s.MESSAGE_AUTHENTICATION_FAILED)

        if not user.is_active or not users_service.password_validation(data_input.password, user.password_hash):
            raise InvalidCredentialsError(s.MESSAGE_AUTHENTICATION_FAILED)

        return UserReadSchema.model_validate(user)

    async def _get_refresh_token_entry(self, session: AsyncSession, data_input: RefreshRequestSchema) -> RefreshTokenReadSchema:
        """Поиск refresh-токена в БД."""
        refresh_token_hash = tokens.hash_token(data_input.refresh_token)

        try:
            refresh_token = await tokens_repo.get_by_refresh_token(session, refresh_token_hash)
        except ObjectNotFoundError:
            raise RefreshTokenNotFoundError(s.MESSAGE_REFRESH_TOKEN_NOT_FOUND)

        refresh_token_dto = RefreshTokenReadSchema.model_validate(refresh_token)
        return refresh_token_dto

    def _refresh_expiry_calc(self) -> datetime:
        """Расчет времени истечения срока жизни токеа."""
        return datetime.now(timezone.utc) + timedelta(days=s.REFRESH_TOKEN_EXPIRES_DAYS)

    def _refresh_token_validation(self, refresh_token_dto: RefreshTokenReadSchema) -> None:
        """Проверка, что данный токен не просрочен."""
        if refresh_token_dto.expires_at < datetime.now(timezone.utc):
            raise RefreshTokenExpiredError(s.MESSAGE_REFRESH_TOKEN_IS_EXPIRED)

    def _user_is_active_check(self, refresh_token_dto: RefreshTokenReadSchema) -> None:
        """Проверка, что пользователь данного токена активен."""
        if not refresh_token_dto.user.is_active:
            raise InvalidCredentialsError(s.MESSAGE_AUTHENTICATION_FAILED)

    def _create_and_hash_refresh_token(self, user_id: int) -> tuple[str, RefreshTokenCreateSchema]:
        """Генерация refresh-токена пользователя и хэширование. Возвращаем сырой токен и хэш."""
        refresh_token = tokens.create_refresh_token()
        refresh_token_hash = tokens.hash_token(refresh_token)
        refresh_token_expiry = self._refresh_expiry_calc()
        return refresh_token, RefreshTokenCreateSchema(user_id=user_id, refresh_token_hash=refresh_token_hash, expires_at=refresh_token_expiry)

    async def _save_refresh_token(self, session: AsyncSession, new_refresh_token_dto: RefreshTokenCreateSchema) -> None:
        """Сохранение refresh-токена пользователя в БД."""
        try:
            await tokens_repo.create(session, new_refresh_token_dto)
        except ObjectNotModifiedError as e:
            raise RefreshTokenCreationError(str(e))

    async def _rotate_refresh_tokens(self, session: AsyncSession, refresh_token_dto: RefreshTokenReadSchema) -> str:
        """Ротация refresh-токенов пользователя. Старый удаляем, новый создаем."""
        raw_token, new_refresh_token_dto = self._create_and_hash_refresh_token(refresh_token_dto.user.id)

        try:
            await tokens_repo.rotate_tokens(session, refresh_token_dto.id, new_refresh_token_dto)
        except ObjectNotFoundError as e:
            raise RefreshTokenDeletionError(str(e))
        except ObjectNotModifiedError as e:
            raise RefreshTokenCreationError(str(e))

        return raw_token

    async def login(self, session: AsyncSession, data_input: LoginRequestSchema) -> TokenPairSchema:
        """Аутентификация пользователя.

        1. Ищем пользователя.
        2. Создаем access-токен.
        3. Создаем, хэшируем, оборачиваем в DTO refresh-токен.
        4. Сохраняем в БД refresh-токен (хэш)
        5. Возвращаем пользователю пару токенов (refresh сырой)
        """
        user = await self._get_user_or_raise(session, data_input)
        access_token = tokens.create_access_token(user.id)

        new_refresh_token, new_refresh_token_dto = self._create_and_hash_refresh_token(user.id)
        await self._save_refresh_token(session, new_refresh_token_dto)

        return TokenPairSchema(access_token=access_token, refresh_token=new_refresh_token)

    async def logout(self, session: AsyncSession, refresh_token: str) -> None:
        """Логаут пользователя.

        1. Хэшируем переданный токен
        2. Ищем запись токена в БД по значению хэша.
        3. Если не нашли, то не очень-то и хотелось.
        4. Если нашли, то удаляем.
        """
        refresh_token_hash = tokens.hash_token(refresh_token)

        try:
            token_dto = await tokens_repo.get_by_refresh_token(session, refresh_token_hash)
            await tokens_repo.delete(session, token_dto.id)
        except ObjectNotFoundError:
            pass

    async def refresh(self, session: AsyncSession, data_input: RefreshRequestSchema) -> TokenPairSchema:
        """Обновление пары access/refresh токенов.

        1. Ищем refresh-токен в БД.
        2. Проверяем, что связанный пользователь активен.
        3. Проверяем, что токен не просрочен.
        4. Создаем access-токен.
        5. Производим ротацию токенов - старый удаляем, новый создаем.
        6. Возвращаем пользователю пару токенов (refresh сырой)
        """
        refresh_token_dto: RefreshTokenReadSchema = await self._get_refresh_token_entry(session, data_input)
        self._user_is_active_check(refresh_token_dto)
        self._refresh_token_validation(refresh_token_dto)

        new_access_token = tokens.create_access_token(refresh_token_dto.user.id)
        new_refresh_token = await self._rotate_refresh_tokens(session, refresh_token_dto)

        return TokenPairSchema(access_token=new_access_token, refresh_token=new_refresh_token)


auth_service = AuthService()
