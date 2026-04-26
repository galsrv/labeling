from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from users.repository import users_repo, roles_repo
from users.schemas import (
    UserReadSchema,
    UserWithHashReadSchema,
    UserCreateSchema,
    UserWithHashCreateSchema,
    UserUpdateSchema,
    UserWithHashUpdateSchema,
    RoleReadSchema,
    RoleCreateSchema,
    RoleUpdateSchema,
)
from users.passwords import passwords


class RolesService(BaseService[RoleReadSchema, RoleCreateSchema, RoleUpdateSchema]):
    """Класс сервисных функций для ролей."""
    read_model = RoleReadSchema
    repo = roles_repo


roles_service = RolesService()


class UsersService(BaseService[UserReadSchema, UserCreateSchema, UserUpdateSchema]):
    """Класс сервисных функций для пользователей."""
    read_model = UserReadSchema
    repo = users_repo

    async def get_by_username(self, session: AsyncSession, username: str) -> UserWithHashReadSchema:
        """Поиск пользователя по юзернейму, возвращает DTO с хешем пароля."""
        user = await users_repo.get_by_username(session, username)
        return UserWithHashReadSchema.model_validate(user)

    def password_validation(self, password_provided: str, password_hash_stored: str) -> bool:
        """Валидация переданного пользователем пароля."""
        return passwords.password_validation(password_provided, password_hash_stored)

    async def create(self, session: AsyncSession, user_dto: UserCreateSchema) -> UserReadSchema:
        """Переопределяем метод создания пользователя в базовом классе, хэшируем переданный пароль и удаляем пароль в исходном виде."""
        payload = user_dto.model_dump(exclude={'password'})
        payload['password_hash'] = passwords.password_hashing(user_dto.password)
        user_dto_with_hash = UserWithHashCreateSchema(**payload)
        return await super().create(session, user_dto_with_hash)

    async def update(self, session: AsyncSession, user_id: int, user_dto: UserUpdateSchema) -> UserReadSchema:
        """Переопределяем метод изменения пользователя в базовом классе, хэшируем переданный пароль и удаляем пароль в исходном виде."""
        if user_dto.password is not None:
            payload = user_dto.model_dump(exclude={'password'})
            payload['password_hash'] = passwords.password_hashing(user_dto.password)
            user_dto_with_hash = UserWithHashUpdateSchema(**payload)
            return await super().update(session, user_id, user_dto_with_hash)

        return await super().update(session, user_id, user_dto)


users_service = UsersService()
