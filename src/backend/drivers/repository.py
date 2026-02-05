from loguru import logger
from sqlalchemy import select

from core.base_repo import BaseRepository, TOrm, AsyncSession
from drivers.models import DriverType
from scales.models import DeviceDriversOrm


class DeviceDriversRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(DeviceDriversOrm)

    async def get_by_type(self, session: AsyncSession, driver_type: DriverType) -> list[TOrm]:
        """Функция чтения единичной записи таблицы."""
        query = select(self.model).where(DeviceDriversOrm.type == driver_type)
        result = await session.execute(query)
        result = result.scalars().all()

        logger.debug(f'Entry retrieve by type {type}: model={self.model.__name__}, {len(result)} entries retrieved')
        return result


drivers_repo = DeviceDriversRepository()
