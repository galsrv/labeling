from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import TOrm


class BaseRepository:
    """Базовый класс методов обращения в БД.

    Не стал делать наследование BaseRepository(Generic[TOrm]) - нужно разобраться в этой логике.
    """
    def __init__(self, model: type[TOrm]) -> None:
        """Инициализация объекта класса."""
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int) -> TOrm | None:
        """Функция чтения единичной записи таблицы."""
        query = select(self.model).where(self.model.id == obj_id)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        success = 'успех' if db_obj else 'объект не найден'
        logger.debug(f'Получен объект БД: модель={self.model.__name__}, id={obj_id}, результат={success}')
        return db_obj

    async def get_all(self, session: AsyncSession) -> list[TOrm]:
        """Метод чтения всех записей таблицы."""
        query = select(self.model).order_by(*self.model.__order_by__)
        result = await session.execute(query)
        result = result.scalars().all()
        logger.debug(f'Получены объекты БД: модель={self.model.__name__}, {len(result)} записей отобрано')
        return result

    # async def create_(self, session: AsyncSession, data_input: BaseModel) -> TOrm:
    #     """Метод создания новой записи в таблице."""
    #     new_db_obj = self.model(**data_input.model_dump())
    #     session.add(new_db_obj)
    #     await session.commit()
    #     await session.refresh(new_db_obj)
    #     logger.debug(f'Entry creation: model={new_db_obj.__class__.__name__}, id={new_db_obj.id}')
    #     return new_db_obj

    async def create(self, session: AsyncSession, data_input: BaseModel) -> int | None:
        """Метод создания новой записи в таблице."""
        new_db_obj = self.model(**data_input.model_dump())
        session.add(new_db_obj)

        try:
            await session.commit()
            await session.refresh(new_db_obj)
            logger.debug(f'Создана запись в БД: модель={new_db_obj.__class__.__name__}, id={new_db_obj.id}')
            return new_db_obj.id
        except IntegrityError as e:
            await session.rollback()
            logger.debug(f'Ошибка создания записи в БД: модель={new_db_obj.__class__.__name__}, ошибка:{str(e)}')
            return None

    # async def update_(self, session: AsyncSession, db_obj: TOrm, data_input: BaseModel) -> TOrm:
    #     """Метод изменения существующей записи таблицы."""
    #     data_input_dict: dict = data_input.model_dump(exclude_none=True)
    #     [setattr(db_obj, k, v) for k, v in data_input_dict.items()]

    #     session.add(db_obj)
    #     await session.commit()
    #     await session.refresh(db_obj)
    #     logger.debug(f'Обновление записи в БД: модель={db_obj.__class__.__name__}, id={db_obj.id}')
    #     return db_obj

    async def update(self, session: AsyncSession, obj_id: int, data_input: BaseModel) -> int | None:
        """Метод изменения существующей записи таблицы, на вход поступает DTO."""
        data_input_dict: dict = data_input.model_dump(exclude_none=True)
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**data_input_dict))

        try:
            await session.execute(stmt)
            await session.commit()
            logger.debug(f'Обновлена запись в БД: модель={self.model.__class__.__name__}, id={obj_id}')
            return obj_id
        except IntegrityError as e:
            await session.rollback()
            logger.debug(f'Ошибка изменения записи в БД: модель={self.model.__class__.__name__}, ошибка:{str(e)}')
            return None

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        """Удаляем запись из таблицы по ключу."""
        query = delete(self.model).where(self.model.id == obj_id)
        await session.execute(query)
        await session.commit()
        logger.debug(f'Удалена запись в БД: модель={self.model.__name__}, id={obj_id}')

    async def delete_all(self, session: AsyncSession) -> None:
        """Удаляем все записи из таблицы."""
        query = delete(self.model)
        await session.execute(query)
        await session.commit()
        logger.debug(f'Удалы все записи модели: {self.model.__name__}')
