from enum import Enum
from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class ScalesOrm(AppBaseClass):
    """Модель справочника весов."""
    __tablename__ = 'scales'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(INET, nullable=False, index=True)  # работает только с postgres
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey(DeviceDriversOrm.id, ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(String(s.DEVICE_DESCRIPTION_MAX_LENGTH), nullable=False)

    driver: Mapped[DeviceDriversOrm] = relationship(DeviceDriversOrm, lazy='joined')
    workplace:  Mapped['WorkplaceOrm'] = relationship('WorkplaceOrm', lazy='joined')

    __table_args__ = (
        CheckConstraint(port >= s.DEVICE_PORT_MIN, name='check_port_min'),
        CheckConstraint(port <= s.DEVICE_PORT_MAX, name='check_port_max'),
    )

    __order_by__ = (id, )


class PrinterOrm(AppBaseClass):
    """Модель справочника принтеров этикеток."""
    __tablename__ = 'printers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(INET, nullable=False, index=True)  # работает только с postgres
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey(DeviceDriversOrm.id, ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(String(s.DEVICE_DESCRIPTION_MAX_LENGTH), nullable=False)

    driver: Mapped[DeviceDriversOrm] = relationship(DeviceDriversOrm, lazy='joined')
    # workplace: Mapped['WorkplaceOrm'] = relationship('WorkplaceOrm', lazy='joined')

    __table_args__ = (
        CheckConstraint(port >= s.DEVICE_PORT_MIN, name='check_port_min'),
        CheckConstraint(port <= s.DEVICE_PORT_MAX, name='check_port_max'),
    )

    __order_by__ = (id, )


class WorkplaceOrm(AppBaseClass):
    """Модель справочника рабочих мест."""
    __tablename__ = 'workplaces'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(s.DEVICE_DESCRIPTION_MAX_LENGTH), nullable=False)
    scales_id: Mapped[int] = mapped_column(Integer, ForeignKey(ScalesOrm.id, ondelete='SET NULL'), nullable=True)
    printer1_id: Mapped[int] = mapped_column(Integer, ForeignKey(PrinterOrm.id, ondelete='SET NULL'), nullable=True)
    printer2_id: Mapped[int] = mapped_column(Integer, ForeignKey(PrinterOrm.id, ondelete='SET NULL'), nullable=True)

    scales: Mapped[ScalesOrm] = relationship(ScalesOrm, lazy='joined')
    #printer1: Mapped[PrinterOrm] = relationship(PrinterOrm, lazy='joined', foreign_keys=['printer1_id'])
    #printer2: Mapped[PrinterOrm] = relationship(PrinterOrm, lazy='joined', foreign_keys=['printer2_id'])

    __order_by__ = (id, )
