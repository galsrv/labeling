from sqlalchemy import CheckConstraint, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings as s
from core.database import AppBaseClass

from device_drivers.drivers import printer_drivers

AVAILABLE_DRIVERS = printer_drivers.keys()


class LabelTemplateORM(AppBaseClass):
    """Модель справочника шаблонов этикеток."""
    __tablename__ = 'label_templates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(s.LABEL_TEMPLATE_NAME_MAX_LENGTH), nullable=False)
    print_command: Mapped[str] = mapped_column(Text, nullable=False)

    driver_name: Mapped[str] = mapped_column(String(s.DRIVER_NAME_MAX_LENGTH), nullable=False, server_default='dpl')

    __table_args__ = (
        CheckConstraint(
            f"driver_name IN ({', '.join(repr(v) for v in AVAILABLE_DRIVERS)})",
            name='check_driver_name_valid',
        ),
    )

    __order_by__ = (id, )
