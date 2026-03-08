from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings as s
from core.database import AppBaseClass

from device_drivers.drivers import printer_drivers

AVAILABLE_DRIVERS = printer_drivers.keys()


class PrinterOrm(AppBaseClass):
    """Модель справочника принтеров этикеток."""
    __tablename__ = 'printers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(INET, nullable=False, index=True)  # работает только с postgres
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(s.DEVICE_DESCRIPTION_MAX_LENGTH), nullable=False)

    driver_name: Mapped[str] = mapped_column(String(s.DRIVER_NAME_MAX_LENGTH), nullable=False)

    __table_args__ = (
        CheckConstraint(port >= s.DEVICE_PORT_MIN, name='check_port_min'),
        CheckConstraint(port <= s.DEVICE_PORT_MAX, name='check_port_max'),
        CheckConstraint(
            f"driver_name IN ({', '.join(repr(v) for v in AVAILABLE_DRIVERS)})",
            name='check_driver_name_valid',
        ),
    )

    __order_by__ = (id, )
