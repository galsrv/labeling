from pydantic import BaseModel, ConfigDict, computed_field

from core.pagination import BasePageSchema
from labels.schemas import LabelTemplatesReadSchema


class ItemReadSchema(BaseModel):
    """Модель представления записи продукта для вывода в HTML."""
    id: int
    name: str
    ingredients: str
    nutrition: str
    fixed_weight: bool
    nominal_weight: float
    min_weight: float
    max_weight: float
    tare_weight: float
    gtin: int
    shelf_life: int
    units_per_box: int
    item_label_template: LabelTemplatesReadSchema

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def nominal_weight_str(self) -> str:
        """Номинальный вес с тремя знаками после запятой."""
        return f"{(self.nominal_weight or 0):.3f}"


class ItemsPageSchema(BasePageSchema):
    """Модель выдачи страницы данных."""
    items: list[ItemReadSchema]
