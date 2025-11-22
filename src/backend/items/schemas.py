from pydantic import BaseModel


class ItemReadSchema(BaseModel):
    """Модель чтения записи продукта."""
    id: int
    name: str
    ingredients: str
    nutrition: str
    fixed_weight: bool
    nominal_weight: float
    min_weight: float
    max_weight: float
    package_weight: float
    gtin: int
    shelf_life: int
    units_per_box: int
