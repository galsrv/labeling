from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings as s
from core.database import AppBaseClass


class ScalesOrm(AppBaseClass):
    """Модель справочника весов."""
    __tablename__ = 'scales'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(INET, nullable=False, index=True)  # работает только с postgres
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(s.DEVICE_DESCRIPTION_MAX_LENGTH), nullable=False)

    driver_name: Mapped[str] = mapped_column(String(s.DRIVER_NAME_MAX_LENGTH), nullable=False)

    __table_args__ = (
        CheckConstraint(port >= s.DEVICE_PORT_MIN, name='check_port_min'),
        CheckConstraint(port <= s.DEVICE_PORT_MAX, name='check_port_max'),
    )

    __order_by__ = (id, )
