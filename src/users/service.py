from sqlalchemy.ext.asyncio import AsyncSession

from core.service import BaseService
from users.passwords import passwords
from users.repository import roles_repo, users_repo
from users.schemas import (
    RoleCreateSchema,
    RoleReadSchema,
    RoleUpdateSchema,
    UserCreateSchema,
    UserPageSchema,
    UserReadSchema,
    UserToSaveCreateSchema,
    UserToSaveUpdateSchema,
    UserUpdateSchema,
    UserWithHashReadSchema,
)


class RolesService(BaseService[RoleReadSchema, RoleCreateSchema, RoleUpdateSchema]):
    """Класс сервисных функций для ролей."""
    read_model = RoleReadSchema
    repo = roles_repo


roles_service = RolesService()


class UsersService(BaseService[UserReadSchema, UserCreateSchema, UserUpdateSchema]):
    """Класс сервисных функций для пользователей."""
    read_model = UserReadSchema
    repo = users_repo

    async def get_page(
            self,
            session: AsyncSession,
            page: int,
            size: int,
        ) -> UserPageSchema:
        """Возвращаем страницу списка пользователей."""
        items, page, pages, size, total = await users_repo.get_page(session, page, size)

        users_page_dto = UserPageSchema(
            items=[UserReadSchema.model_validate(item) for item in items],
            page=page,
            pages=pages,
            size=size,
            total=total,
        )
        return users_page_dto

    async def get_by_username(self, session: AsyncSession, username: str) -> UserWithHashReadSchema:
        """Поиск пользователя по юзернейму, возвращает DTO с хешем пароля."""
        user = await users_repo.get_by_username(session, username)
        return UserWithHashReadSchema.model_validate(user)

    def password_validation(self, password_provided: str, password_hash_stored: str) -> bool:
        """Валидация переданного пользователем пароля."""
        return passwords.password_validation(password_provided, password_hash_stored)

    async def create(self, session: AsyncSession, user_dto: UserCreateSchema, current_user: UserReadSchema) -> UserReadSchema:
        """Переопределяем метод создания пользователя в базовом классе.

        1. Убираем сырой пароль из словаря
        2. Хэшируем сырой пароль
        3. Формируем корректный DTO, подставляем автора
        4. Выполняем метод базового класса
        """
        payload = user_dto.model_dump(exclude={'password'})
        payload['password_hash'] = passwords.password_hashing(user_dto.password)

        user_to_create_dto = UserToSaveCreateSchema(**payload, created_by_id=current_user.id, updated_by_id=current_user.id)
        return await super().create(session, user_to_create_dto)

    async def update(self, session: AsyncSession, user_id: int, user_dto: UserUpdateSchema, current_user: UserReadSchema) -> UserReadSchema:
        """Переопределяем метод изменения пользователя в базовом классе.

        1. Убираем сырой пароль из словаря
        2. Если пароль был передан, хэшируем новый сырой пароль
        3. Формируем корректный DTO, подставляем автора
        4. Выполняем метод базового класса
        """
        payload = user_dto.model_dump(exclude={'password'})

        if user_dto.password is not None:
            payload['password_hash'] = passwords.password_hashing(user_dto.password)

        user_to_save_dto = UserToSaveUpdateSchema(**payload, updated_by_id=current_user.id)
        return await super().update(session, user_id, user_to_save_dto)


users_service = UsersService()
