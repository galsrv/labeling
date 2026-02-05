from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings as s
from core.database import AppBaseClass

from drivers.models import DeviceDriversOrm


class ScalesOrm(AppBaseClass):
    """Модель справочника весов."""
    __tablename__ = 'scales'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(INET, nullable=False, index=True)  # работает только с postgres
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey(DeviceDriversOrm.id, ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(String(s.DEVICE_DESCRIPTION_MAX_LENGTH), nullable=False)

    driver: Mapped[DeviceDriversOrm] = relationship(DeviceDriversOrm, lazy='joined')
    # workplace:  Mapped['WorkplaceOrm'] = relationship('WorkplaceOrm', lazy='joined')

    __table_args__ = (
        CheckConstraint(port >= s.DEVICE_PORT_MIN, name='check_port_min'),
        CheckConstraint(port <= s.DEVICE_PORT_MAX, name='check_port_max'),
    )

    __order_by__ = (id, )
