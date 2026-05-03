from datetime import date, timedelta

from pydantic import BaseModel, ConfigDict, field_validator

from core.config import settings as s
from core.pagination import BasePageSchema
from items.schemas import ItemReadSchema
from orders.models import OrderStatus


class OrderReadSchema(BaseModel):
    """Модель представления задания на производство."""
    id: int
    status: OrderStatus
    production_date: date
    expiration_date: date
    ordered_kg: float
    produced_kg: float
    produced_boxes: int
    item: ItemReadSchema

    model_config = ConfigDict(from_attributes=True)


class OrderPageSchema(BasePageSchema):
    """Модель выдачи страницы данных."""
    items: list[OrderReadSchema]


class OrderCreateSchema(BaseModel):
    """Модель создания задания на производство."""
    item_id: int
    production_date: date
    expiration_date: date
    ordered_kg: float

    model_config = ConfigDict(from_attributes=True)

    @field_validator('production_date', mode='after')
    @classmethod
    def production_date_range(cls, value: date) -> date:
        """Дата производства не может быть в прошлом или даелком будущем."""
        today = date.today()
        min_date = today - timedelta(days=s.ORDER_PRODUCTION_DATE_DEPTH_BACK)
        max_date = today + timedelta(days=s.ORDER_PRODUCTION_DATE_DEPTH_FORWARD)

        if not min_date <= value <= max_date:
            raise ValueError(s.MESSAGE_ORDER_WRONG_PRODUCTION_DATE)

        return value


class OrderUpdateSchema(BaseModel):
    """Модель изменения задания на производство."""
    status: OrderStatus | None = None
    produced_kg: float | None = None
    produced_boxes: int | None = None

    model_config = ConfigDict(from_attributes=True)
