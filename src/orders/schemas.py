from datetime import date, timedelta
from pydantic import BaseModel, ConfigDict, computed_field, field_validator

from core.config import settings as s

from items.schemas import ItemReadSchema, ItemWebSchema
from orders.models import OrderStatus


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


class OrderWebSchema(BaseModel):
    """Модель представления записи задания на производство для вывода в HTML."""
    id: int
    status: OrderStatus
    production_date: date
    expiration_date: date
    ordered_kg: float
    produced_kg: float
    produced_boxes: int
    item: ItemWebSchema

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def status_label(self) -> str:
        """Сокращение переменной со статусом .value."""
        return self.status.value

    @computed_field
    @property
    def production_date_str(self) -> str:
        """Дата производства в виде текста."""
        return self.production_date.strftime("%d.%m.%Y")

    @computed_field
    @property
    def ordered_kg_str(self) -> str:
        """Заказанное количество с тремя знаками после запятой."""
        return f"{(self.ordered_kg or 0):.3f}"

    @computed_field
    @property
    def produced_kg_str(self) -> str:
        """Произведенное количество с тремя знаками после запятой."""
        return f"{(self.produced_kg or 0):.3f}"

    @computed_field
    @property
    def progress_pct(self) -> int:
        """Процент выполнения задания."""
        ordered = self.ordered_kg or 0
        produced = self.produced_kg or 0
        if ordered <= 0:
            return 0
        pct = int(round((produced / ordered) * 100))
        return 0 if pct < 0 else 100 if pct > 100 else pct

    @computed_field
    @property
    def progress_bar_class(self) -> str:
        """Класс для визуализации статуса задания "Создано", "Активно", "Закрыто"."""
        if self.status == OrderStatus.CLOSED:
            return "bg-success"
        if self.status == OrderStatus.ACTIVE:
            return ""  # синий по умолчанию для bootstrap
        return "bg-secondary"
