from sqlalchemy import ForeignKey, Integer, String

from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings as s
from core.database import AppBaseClass

from printers.models import PrinterOrm
from scales.models import ScalesOrm


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
