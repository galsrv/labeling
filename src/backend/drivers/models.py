from enum import Enum
from sqlalchemy import Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings as s
from core.database import AppBaseClass


class DriverType(Enum):
    """Возможные типы драйверов устройств."""
    PRINTER = 'PRINTER'
    SCALES = 'SCALES'


class DeviceDriversOrm(AppBaseClass):
    """Модель справочника драйверов весов и принтеров."""
    __tablename__ = 'drivers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(s.DRIVER_NAME_MAX_LENGTH), nullable=False, unique=True)
    type: Mapped[DriverType] = mapped_column(
        SQLEnum(DriverType, name='device_driver_enum'), default=DriverType.SCALES, nullable=False)

    __order_by__ = (id, )
