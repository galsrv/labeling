from datetime import date
from pydantic import BaseModel, ConfigDict, computed_field

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
