from pydantic import BaseModel, ConfigDict

from scales.schemas import ScalesReadWebSchema


class WorkplaceReadWebSchema(BaseModel):
    """Модель представления записи рабочего места для вывода в HTML."""
    id: int
    description: str
    scales: ScalesReadWebSchema

    model_config = ConfigDict(from_attributes=True)
