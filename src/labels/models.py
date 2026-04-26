from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings as s
from database.config import AppBaseClass


class LabelTemplateORM(AppBaseClass):
    """Модель справочника шаблонов этикеток."""
    __tablename__ = 'label_templates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(s.LABEL_TEMPLATE_NAME_MAX_LENGTH), nullable=False)
    print_command: Mapped[str] = mapped_column(Text, nullable=False)

    driver_name: Mapped[str] = mapped_column(String(s.DRIVER_NAME_MAX_LENGTH), nullable=False, server_default='dpl')

    __order_by__ = (id, )
