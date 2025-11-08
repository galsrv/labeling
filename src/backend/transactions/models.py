from datetime import date
from enum import Enum

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Integer, Enum as SQLEnum, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import AppBaseClass
from items.models import ItemsOrm

class OrderStatus(Enum):
    CREATED = 'CREATED'
    ACTIVE = 'ACTIVE'
    CLOSED = 'CLOSED'

class OrderOrm(AppBaseClass):
    """Модель заказов на производство."""
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey(ItemsOrm.id, ondelete='CASCADE'))
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name='order_status_enum'), default=OrderStatus.CREATED, nullable=False)

    production_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiration_date: Mapped[date] = mapped_column(Date, nullable=False)

    produced_kg: Mapped[float] = mapped_column(Float, default=0, server_default=text('0'))
    produced_boxes: Mapped[int] = mapped_column(Integer, default=0, server_default=text('0'))

    item: Mapped[ItemsOrm] = relationship(ItemsOrm, lazy='joined')

    __table_args__ = (
        CheckConstraint(
            "production_date >= CURRENT_DATE - INTERVAL '1 day' AND production_date <= CURRENT_DATE + INTERVAL '30 day'",
            name="production_date_range"
        ),
    )

    __order_by__ = (id, )
