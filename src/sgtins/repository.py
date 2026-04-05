from loguru import logger
from sqlalchemy import BigInteger, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_repo import BaseRepository
from sgtins.models import SgtinOrm, SgtinStatus


class SgtinRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(SgtinOrm)

    async def get_all_by_gtin(self, session: AsyncSession, gtin: int) -> list:
        """Метод получения всех значений поля GTIN.

        Недостаток реализации - GTIN в продуктах число, в кодах маркировки - строка.
        """
        query = select(SgtinOrm).where(
            cast(SgtinOrm.gtin, BigInteger) == gtin,
            SgtinOrm.status == SgtinStatus.ISSUED
        ).order_by(SgtinOrm.created_at)

        gtins = await session.execute(query)
        gtins = gtins.scalars().all()

        logger.debug(f'Получение доступных кодов маркировки по GTIN, число отобранных записей {len(gtins)}')
        return gtins

    # async def batch_status_change(self, session: AsyncSession, ids: list[int], status_to_set: SgtinStatus = SgtinStatus.PRINTED) -> bool:
    #     """Массовая смена статуса кодов маркировки."""
    #     query = update(SgtinOrm).where(SgtinOrm.id.in_(ids)).values(status=status_to_set)

    #     try:
    #         await session.execute(query)
    #         await session.commit()
    #         logger.debug(f'Обновлен статус кодов маркировки, число кодов {len(ids)}')
    #         return True
    #     except IntegrityError as e:
    #         await session.rollback()
    #         logger.debug(f'Ошибка изменения статуса кодов маркировки: {str(e)}')
    #         return False


sgtin_repo = SgtinRepository()
