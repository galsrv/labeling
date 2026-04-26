from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.repository import BaseRepository
from items.models import ItemsOrm


class ItemsRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(ItemsOrm)

    async def get_by_gtin(self, session: AsyncSession, gtin: int) -> ItemsOrm | None:
        """Метод поиска записи по полю GTIN."""
        query = select(ItemsOrm).where(ItemsOrm.gtin == gtin)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        success = 'успех' if db_obj else 'объект не найден'
        logger.debug(f'Получение объекта БД: модель={ItemsOrm.__name__}, gtin={gtin}, результат={success}')
        return db_obj

    async def get_all_gtins(self, session: AsyncSession) -> list:
        """Метод получения всех значений поля GTIN."""
        query = select(ItemsOrm.gtin).distinct()
        gtins = await session.execute(query)
        gtins = gtins.scalars().all()

        logger.debug(f'Получение всех значений поля GTIN мз модели {ItemsOrm.__name__}, число записей {len(gtins)}')
        return gtins


items_repo = ItemsRepository()
