from enum import Enum

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings as s
from core.database import AppBaseClass

class ScalesDriver(Enum):
    TENZO_M = 'tenzo_m'

class ScalesOrm(AppBaseClass):
    """Модель справочника весов."""
    __tablename__ = 'scales'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(INET, nullable=False, index=True) # работает только с postgres
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    driver: Mapped[ScalesDriver] = mapped_column(SQLEnum(ScalesDriver, name='scales_driver_enum'), nullable=False)
    description: Mapped[str] = mapped_column(String(s.SCALES_DESCRIPTION_MAX_LENGTH), nullable=False)

    __table_args__ = (
        CheckConstraint(port >= s.SCALES_PORT_MIN, name='check_port_min'),
        CheckConstraint(port <= s.SCALES_PORT_MAX, name='check_port_max'),
    )

    __order_by__ = (id, )

class WorkplaceOrm(AppBaseClass):
    """Модель справочника рабочих мест."""
    __tablename__ = 'workplaces'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(s.SCALES_DESCRIPTION_MAX_LENGTH), nullable=False)
    scales_id: Mapped[int] = mapped_column(Integer, ForeignKey(ScalesOrm.id, ondelete='SET NULL'))

    scales: Mapped[ScalesOrm] = relationship(ScalesOrm, lazy='joined')

    __order_by__ = (id, )