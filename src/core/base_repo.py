from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.database import TOrm
from core.exceptions import ObjectNotFound, ObjectNotModified


class BaseRepository:
    """Базовый класс методов обращения в БД.

    Не стал делать наследование BaseRepository(Generic[TOrm]) - нужно разобраться в этой логике.
    """
    def __init__(self, model: type[TOrm]) -> None:
        """Инициализация объекта класса."""
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int) -> TOrm:
        """Функция чтения единичной записи таблицы."""
        query = select(self.model).where(self.model.id == obj_id)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        if db_obj is None:
            message = f'{s.MESSAGE_ENTRY_DOESNT_EXIST}: {self.model.__name__}, id={obj_id}'
            logger.debug(message)
            raise ObjectNotFound(message)

        logger.debug(f'Получение объекта БД: модель={self.model.__name__}, id={obj_id}')
        return db_obj

    async def get_all(self, session: AsyncSession) -> list[TOrm]:
        """Метод чтения всех записей таблицы."""
        query = select(self.model).order_by(*self.model.__order_by__)
        result = await session.execute(query)
        result = result.scalars().all()
        logger.debug(f'Получены объекты БД: модель={self.model.__name__}, {len(result)} записей отобрано')
        return result

    async def create(self, session: AsyncSession, data_input: BaseModel) -> TOrm:
        """Метод создания новой записи в таблице."""
        new_db_obj = self.model(**data_input.model_dump())
        session.add(new_db_obj)

        try:
            await session.commit()
            await session.refresh(new_db_obj)
            logger.debug(f'Создана запись в БД: модель={new_db_obj.__class__.__name__}, id={new_db_obj.id}')
            return new_db_obj

        except IntegrityError as e:
            await session.rollback()
            logger.debug(f'Ошибка создания записи в БД: модель={new_db_obj.__class__.__name__}, ошибка:{str(e)}')
            raise ObjectNotModified(str(e))

    async def update(self, session: AsyncSession, obj_id: int, data_input: BaseModel) -> TOrm:
        """Метод изменения существующей записи таблицы, на вход поступает DTO."""
        data_input_dict: dict = data_input.model_dump(exclude_none=True)
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**data_input_dict))

        try:
            result = await session.execute(stmt)

            if result.rowcount == 0:
                await session.rollback()
                message = f'{s.MESSAGE_ENTRY_DOESNT_EXIST}: {self.model.__name__}, id={obj_id}'
                logger.debug(message)
                raise ObjectNotFound(message)

            await session.commit()
            logger.debug(f'Обновлена запись в БД: модель={self.model.__class__.__name__}, id={obj_id}')
            return await self.get(session, obj_id)

        except IntegrityError as e:
            await session.rollback()
            logger.debug(f'Ошибка изменения записи в БД: модель={self.model.__class__.__name__}, ошибка:{str(e)}')
            raise ObjectNotModified(str(e))

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        """Удаляем запись из таблицы по ключу."""
        query = delete(self.model).where(self.model.id == obj_id)
        result = await session.execute(query)

        if result.rowcount == 0:
            await session.rollback()
            message = f'{s.MESSAGE_ENTRY_DOESNT_EXIST}: {self.model.__name__}, id={obj_id}'
            logger.debug(message)
            raise ObjectNotFound(message)

        await session.commit()
        logger.debug(f'Удалена запись в БД: модель={self.model.__name__}, id={obj_id}')

    async def delete_all(self, session: AsyncSession) -> None:
        """Удаляем все записи из таблицы."""
        query = delete(self.model)
        await session.execute(query)
        await session.commit()
        logger.debug(f'Удалены все записи модели: {self.model.__name__}')

    async def batch_create(self, session: AsyncSession, data_input_list: list[BaseModel]) -> bool:
        """Метод пакетного создания записей в таблице."""
        if not data_input_list:
            return True

        new_db_objects = [self.model(**data_input.model_dump()) for data_input in data_input_list]
        session.add_all(new_db_objects)

        try:
            await session.commit()
            logger.debug(f'Созданы записи в БД: модель={self.model.__name__}, количество={len(new_db_objects)}')
            return True
        except IntegrityError as e:
            await session.rollback()
            logger.debug(f'Ошибка пакетного создания записей в БД: модель={self.model.__name__}, ошибка:{str(e)}')
            return False

    async def batch_update(self, session: AsyncSession, ids: list[int], data_input: BaseModel) -> bool:
        """Массовая смена статуса кодов маркировки."""
        data_input_dict: dict = data_input.model_dump(exclude_none=True)

        query = update(self.model).where(self.model.id.in_(ids)).values(**data_input_dict)

        try:
            await session.execute(query)
            await session.commit()
            logger.debug(f'Обновлено {len(ids)} записей в БД: модель={self.model.__class__.__name__}')
            return True
        except IntegrityError as e:
            await session.rollback()
            logger.debug(f'Ошибка изменения записей в БД: модель={self.model.__class__.__name__}, ошибка:{str(e)}')
            return False
