from typing import Any

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Базовый класс сервисных методов обращения в БД."""
    def __init__(self, model) -> None:  # noqa: ANN001
        """Инициализация объекта класса."""
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int) -> Any | None:
        """Функция чтения единичной записи таблицы."""
        query = select(self.model).where(self.model.id == obj_id)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        success = 'success' if db_obj else 'not found'
        logger.debug(f'Entry retrieve: model={self.model.__name__}, id={obj_id}, result={success}')
        return db_obj

    async def get_all(self, session: AsyncSession) -> list:
        """Метод чтения всех записей таблицы."""
        query = select(self.model).order_by(*self.model.__order_by__)
        result = await session.execute(query)
        result = result.scalars().all()
        logger.debug(f'Entry retrieve: model={self.model.__name__}, {len(result)} entries retrieved')
        return result  # pyright: ignore[reportReturnType]

    async def create(self, session: AsyncSession, data_input: BaseModel):  # noqa: ANN201
        """Метод создания новой записи в таблице."""
        new_db_obj = self.model(**data_input.model_dump())
        session.add(new_db_obj)
        await session.commit()
        await session.refresh(new_db_obj)
        logger.debug(f'Entry creation: model={new_db_obj.__class__.__name__}, id={new_db_obj.id}')
        return new_db_obj

    async def update(self, session: AsyncSession, db_obj, data_input: BaseModel):  # noqa: ANN001, ANN201
        """Метод изменения существующей записи таблицы."""
        data_input_dict: dict = data_input.model_dump(exclude_none=True)
        [setattr(db_obj, k, v) for k, v in data_input_dict.items()]

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        logger.debug(
            f'Entry update: model={db_obj.__class__.__name__}, id={db_obj.id}')
        return db_obj

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        """Удаляем запись из таблицы по ключу."""
        query = delete(self.model).where(self.model.id == obj_id)
        await session.execute(query)
        await session.commit()
        logger.debug(
            f'Entry deletion: model={self.model.__name__}, id={obj_id}')

    async def delete_all(self, session: AsyncSession) -> None:
        """Удаляем все записи из таблицы."""
        query = delete(self.model)
        await session.execute(query)
        await session.commit()
        logger.debug(
            f'All data from model={self.model.__name__} have been deleted')
