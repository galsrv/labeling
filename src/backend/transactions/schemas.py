from datetime import date
from pydantic import BaseModel, ConfigDict

from items.schemas import ItemReadSchema
from transactions.models import OrderStatus


class OrderReadSchema(BaseModel):
    """Модель представления записи задания на производство для вывода в API."""
    id: int
    status: OrderStatus
    production_date: date
    expiration_date: date
    ordered_kg: float
    produced_kg: float
    produced_boxes: int
    item: ItemReadSchema

    model_config = ConfigDict(from_attributes=True)


class OrderWebSchema(BaseModel):
    """Модель представления записи задания на производство для вывода в HTML."""
    id: int
    status: OrderStatus
    production_date: date
    expiration_date: date
    ordered_kg: float
    produced_kg: float
    produced_boxes: int
    item: ItemReadSchema

    model_config = ConfigDict(from_attributes=True)
