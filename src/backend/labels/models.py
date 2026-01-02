from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings as s
from core.database import AppBaseClass
from workplaces.models import DeviceDriversOrm


class LabelTemplate(AppBaseClass):
    """Модель справочника шаблонов этикеток."""
    __tablename__ = 'label_templates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(s.LABEL_TEMPLATE_NAME_MAX_LENGTH), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey(DeviceDriversOrm.id, ondelete='CASCADE'))
    print_command: Mapped[str] = mapped_column(Text, nullable=False)

    driver: Mapped[DeviceDriversOrm] = relationship(DeviceDriversOrm, lazy='joined')

    __order_by__ = (id, )
