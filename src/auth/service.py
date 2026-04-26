from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from database.exceptions import ObjectNotFound, ObjectNotModified
from auth.exceptions import (
    InvalidCredentialsError,
    RefreshTokenDeletionError,
    RefreshTokenExpiredError,
    RefreshTokenCreationError,
    RefreshTokenNotFoundError,
)
from auth.schemas import LoginRequestSchema, RefreshRequestSchema, RefreshTokenReadSchema, TokenPairSchema, RefreshTokenCreateSchema
from auth.repository import tokens_repo
from auth.tokens import tokens
from users.schemas import UserReadSchema, UserWithHashReadSchema
from users.service import users_service


class AuthService():
    """Класс серсивных методов модуля аутентификации."""

    async def _get_user_or_raise(self, session: AsyncSession, data_input: LoginRequestSchema) -> UserReadSchema:
        """Проверка введенной пары юзернейм-пароль."""
        try:
            user: UserWithHashReadSchema = await users_service.get_by_username(session, data_input.username)
        except ObjectNotFound:
            raise InvalidCredentialsError(s.MESSAGE_AUTHENTICATION_FAILED)

        if not user.is_active or not users_service.password_validation(data_input.password, user.password_hash):
            raise InvalidCredentialsError(s.MESSAGE_AUTHENTICATION_FAILED)

        return UserReadSchema.model_validate(user)

    async def _get_refresh_token_entry(self, session: AsyncSession, data_input: RefreshRequestSchema) -> RefreshTokenReadSchema:
        """Поиск refresh-токена в БД."""
        refresh_token_hash = tokens.hash_token(data_input.refresh_token)

        try:
            refresh_token = await tokens_repo.get_by_refresh_token(session, refresh_token_hash)
        except ObjectNotFound:
            raise RefreshTokenNotFoundError(s.MESSAGE_REFRESH_TOKEN_NOT_FOUND)

        refresh_token_dto = RefreshTokenReadSchema.model_validate(refresh_token)
        return refresh_token_dto

    def _refresh_expiry(self) -> datetime:
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

    def _generate_refresh_token(self, user_id: int) -> tuple[str, RefreshTokenCreateSchema]:
        """Генерация сырого refresh-токена пользователя и хэширование."""
        refresh_token = tokens.create_refresh_token()
        refresh_token_hash = tokens.hash_token(refresh_token)
        refresh_token_expiry = self._refresh_expiry()
        return refresh_token, RefreshTokenCreateSchema(user_id=user_id, refresh_token_hash=refresh_token_hash, expires_at=refresh_token_expiry)

    async def _create_refresh_token(self, session: AsyncSession, user: UserReadSchema) -> str:
        """Создание refresh-токена пользователя. Хэширование, сохранение хэша в БД."""
        raw_token, new_refresh_token_dto = self._generate_refresh_token(user.id)
        try:
            await tokens_repo.create(session, new_refresh_token_dto)
        except ObjectNotModified as e:
            raise RefreshTokenCreationError(str(e))

        return raw_token

    async def _create_new_refresh_token_and_delete_old_one(self, session: AsyncSession, refresh_token_dto: RefreshTokenReadSchema) -> str:
        """Создание refresh-токена пользователя. Хэширование, сохранение хэша в БД. Удаление старого токена."""
        raw_token, new_refresh_token_dto = self._generate_refresh_token(refresh_token_dto.user.id)
        try:
            await tokens_repo.create_new_and_delete_old_token(session, refresh_token_dto.id, new_refresh_token_dto)
        except ObjectNotFound as e:
            raise RefreshTokenDeletionError(str(e))
        except ObjectNotModified as e:
            raise RefreshTokenCreationError(str(e))

        return raw_token

    async def login(self, session: AsyncSession, data_input: LoginRequestSchema) -> TokenPairSchema:
        """Аутентификация пользователя."""
        user = await self._get_user_or_raise(session, data_input)
        access_token = tokens.create_access_token(user.id)
        refresh_token = await self._create_refresh_token(session, user)
        return TokenPairSchema(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, session: AsyncSession, data_input: RefreshRequestSchema) -> TokenPairSchema:
        """Обновление пары access/refresh токенов."""
        refresh_token_dto: RefreshTokenReadSchema = await self._get_refresh_token_entry(session, data_input)
        self._user_is_active_check(refresh_token_dto)
        self._refresh_token_validation(refresh_token_dto)

        new_access_token = tokens.create_access_token(refresh_token_dto.user.id)
        new_refresh_token = await self._create_new_refresh_token_and_delete_old_one(session, refresh_token_dto)

        return TokenPairSchema(access_token=new_access_token, refresh_token=new_refresh_token)


auth_service = AuthService()
