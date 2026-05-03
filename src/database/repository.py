import math

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from database.config import TOrm
from database.exceptions import ObjectNotFoundError, ObjectNotModifiedError


class BaseRepository:
    """Базовый класс методов обращения в БД."""

    def __init__(self, model: type[TOrm]) -> None:
        """Инициализация объекта класса."""
        self.model = model

    async def get_page(
            self,
            session: AsyncSession,
            page: int,
            size: int,
        ) -> tuple[list[TOrm], int, int, int, int]:
        """Метод чтения записей таблицы с ограничением по числе возвращаемых записей.

        Рассчитываем данные для корректной пагинации - total & pages
        """
        count_query = select(func.count()).select_from(self.model)
        total = await session.scalar(count_query) or 0
        pages = math.ceil(total / size) if total else 0

        query = (
            select(self.model)
            .order_by(*self.model.__order_by__)
            .offset((page - 1) * size)
            .limit(size)
        )

        result = await session.execute(query)
        items = list(result.scalars().all())
        logger.debug(s.MESSAGE_DB_OBJECT_GET_MULTI.format(model=self.model.__name__, number=len(items)))

        return items, page, pages, size, total

    async def get_all(self, session: AsyncSession) -> list[TOrm]:
        """Метод чтения всех записей таблицы."""
        query = select(self.model).order_by(*self.model.__order_by__)
        result = await session.execute(query)
        result = result.scalars().all()
        logger.debug(s.MESSAGE_DB_OBJECT_GET_MULTI.format(model=self.model.__name__, number=len(result)))
        return result

    async def get(self, session: AsyncSession, obj_id: int) -> TOrm:
        """Функция чтения единичной записи таблицы."""
        query = select(self.model).where(self.model.id == obj_id)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        if db_obj is None:
            message = s.MESSAGE_DB_OBJECT_DOESNT_EXIST.format(model=self.model.__name__, obj_id=obj_id)
            logger.debug(message)
            raise ObjectNotFoundError(message)

        logger.debug(s.MESSAGE_DB_OBJECT_GET.format(model=self.model.__name__, obj_id=obj_id))

        return db_obj

    async def create(self, session: AsyncSession, data_input: BaseModel) -> TOrm:
        """Метод создания новой записи в таблице."""
        new_db_obj = self.model(**data_input.model_dump())
        session.add(new_db_obj)

        try:
            await session.commit()
            await session.refresh(new_db_obj)
            logger.debug(s.MESSAGE_DB_OBJECT_CREATE.format(model=self.model.__name__, obj_id=new_db_obj.id))
            return new_db_obj

        except IntegrityError as e:
            await session.rollback()
            logger.debug(s.MESSAGE_DB_OBJECT_CREATE_ERROR.format(model=self.model.__name__, error=str(e)))
            raise ObjectNotModifiedError(str(e))

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
                message = s.MESSAGE_DB_OBJECT_DOESNT_EXIST.format(model=self.model.__name__, obj_id=obj_id)
                logger.debug(message)
                raise ObjectNotFoundError(message)

            await session.commit()
            logger.debug(s.MESSAGE_DB_OBJECT_UPDATE.format(model=self.model.__name__, obj_id=obj_id))
            return await self.get(session, obj_id)

        except IntegrityError as e:
            await session.rollback()
            logger.debug(s.MESSAGE_DB_OBJECT_UPDATE_ERROR.format(model=self.model.__name__, error=str(e)))
            raise ObjectNotModifiedError(str(e))

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        """Удаляем запись из таблицы по ключу."""
        query = delete(self.model).where(self.model.id == obj_id)
        result = await session.execute(query)

        if result.rowcount == 0:
            await session.rollback()
            message = s.MESSAGE_DB_OBJECT_DOESNT_EXIST.format(model=self.model.__name__, obj_id=obj_id)
            logger.debug(message)
            raise ObjectNotFoundError(message)

        await session.commit()
        logger.debug(s.MESSAGE_DB_OBJECT_DELETE.format(model=self.model.__name__, obj_id=obj_id))

    async def delete_all(self, session: AsyncSession) -> None:
        """Удаляем все записи из таблицы."""
        query = delete(self.model)
        await session.execute(query)
        await session.commit()
        logger.debug(s.MESSAGE_DB_OBJECT_DELETE_ALL.format(model=self.model.__name__))

    async def batch_create(self, session: AsyncSession, data_input_list: list[BaseModel]) -> bool:
        """Метод пакетного создания записей в таблице."""
        if not data_input_list:
            return True

        new_db_objects = [self.model(**data_input.model_dump()) for data_input in data_input_list]
        session.add_all(new_db_objects)

        try:
            await session.commit()
            logger.debug(s.MESSAGE_DB_OBJECT_CREATE_MULTI.format(model=self.model.__name__, number=len(new_db_objects)))
            return True
        except IntegrityError as e:
            await session.rollback()
            logger.debug(s.MESSAGE_DB_OBJECT_CREATE_ERROR.format(model=self.model.__name__, error=str(e)))
            return False

    async def batch_update(self, session: AsyncSession, ids: list[int], data_input: BaseModel) -> bool:
        """Массовая смена статуса кодов маркировки."""
        data_input_dict: dict = data_input.model_dump(exclude_none=True)

        query = update(self.model).where(self.model.id.in_(ids)).values(**data_input_dict)

        try:
            await session.execute(query)
            await session.commit()
            logger.debug(s.MESSAGE_DB_OBJECT_CREATE_MULTI.format(model=self.model.__name__, number=len(ids)))
            return True
        except IntegrityError as e:
            await session.rollback()
            logger.debug(s.MESSAGE_DB_OBJECT_UPDATE_ERROR.format(model=self.model.__name__, error=str(e)))
            return False
