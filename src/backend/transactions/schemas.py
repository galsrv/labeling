from datetime import date
from pydantic import BaseModel

from items.schemas import ItemReadSchema
from transactions.models import OrderStatus

class OrderReadSchema(BaseModel):
    """Модель чтения записи заказа на производство."""
    id: int
    status: OrderStatus
    production_date: date
    expiration_date: date
    produced_kg: float
    produced_boxes: int
    item: ItemReadSchema