from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, BigInteger, String, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings as s
from core.database import AppBaseClass
from labels.models import LabelTemplateORM


class ItemsOrm(AppBaseClass):
    """Модель справочника продуктов."""
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(s.ITEM_NAME_MAX_LENGTH), nullable=False)
    ingredients: Mapped[str] = mapped_column(String(s.ITEM_INGRIDIENTS_MAX_LENGTH))
    nutrition: Mapped[str] = mapped_column(String(s.ITEM_NUTRITION_MAX_LENGTH))
    fixed_weight: Mapped[bool] = mapped_column(Boolean, nullable=False)
    nominal_weight: Mapped[float] = mapped_column(Float, nullable=False)
    min_weight: Mapped[float] = mapped_column(Float, nullable=False)
    max_weight: Mapped[float] = mapped_column(Float, nullable=False)
    gtin: Mapped[int] = mapped_column(BigInteger, nullable=False)
    shelf_life: Mapped[int] = mapped_column(Integer, nullable=False)
    units_per_box: Mapped[int] = mapped_column(Integer, nullable=False)
    tare_weight: Mapped[float] = mapped_column(Float, nullable=False)
    item_label_template_id: Mapped[int] = mapped_column(Integer, ForeignKey(LabelTemplateORM.id, ondelete='SET NULL'), nullable=True)

    item_label_template: Mapped[LabelTemplateORM] = relationship(LabelTemplateORM, lazy='joined')

    __table_args__ = (
        CheckConstraint(gtin >= s.ITEM_GTIN_MIN_VALUE, name='check_gtin_min'),
        CheckConstraint(gtin <= s.ITEM_GTIN_MAX_VALUE, name='check_gtin_max'),
        CheckConstraint(units_per_box >= 1, name='check_units_per_box_min'),
        Index('ix_items_name', 'name'),
        UniqueConstraint('gtin', name='unique_items_gtin'),  # Индекс добавляется автоматически
    )

    __order_by__ = (id, )
