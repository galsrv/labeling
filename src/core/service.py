from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.repository import BaseRepository

TRead = TypeVar('TRead', bound=BaseModel)
TCreate = TypeVar('TCreate', bound=BaseModel)
TUpdate = TypeVar('TUpdate', bound=BaseModel)


class BaseService(Generic[TRead, TCreate, TUpdate]):
    """Базовый класс сервисных функций."""
    read_model: type[TRead]
    repo: BaseRepository

    async def get_all(self, session: AsyncSession) -> list[TRead]:
        """Возвращаем все объекты модели."""
        objects = await self.repo.get_all(session)
        objects_dto = [self.read_model.model_validate(obj) for obj in objects]
        return objects_dto

    async def get(self, session: AsyncSession, obj_id: int) -> TRead:
        """Возвращаем объект по его id."""
        obj = await self.repo.get(session, obj_id)
        obj_dto = self.read_model.model_validate(obj)
        return obj_dto

    async def create(self, session: AsyncSession, obj_dto: TCreate) -> TRead:
        """Создаем объект, возвращаем его."""
        obj_orm = await self.repo.create(session, obj_dto)
        return self.read_model.model_validate(obj_orm)

    async def update(self, session: AsyncSession, obj_id: int, obj_dto: TUpdate) -> TRead:
        """Изменяем объект, возвращаем его."""
        obj_orm = await self.repo.update(session, obj_id, obj_dto)
        return self.read_model.model_validate(obj_orm)

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        """Удаляем объект, ничего не возвращаем."""
        await self.repo.delete(session, obj_id)
