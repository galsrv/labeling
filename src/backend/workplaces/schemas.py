from pydantic import BaseModel, ConfigDict

from scales.schemas import ScalesReadSchema, ScalesWebSchema


class WorkplaceReadSchema(BaseModel):
    """Модель представления записи рабочего места для вывода в API."""
    id: int
    description: str
    scales: ScalesReadSchema

    model_config = ConfigDict(from_attributes=True)


class WorkplaceWebSchema(BaseModel):
    """Модель представления записи рабочего места для вывода в HTML."""
    id: int
    description: str
    scales: ScalesWebSchema

    model_config = ConfigDict(from_attributes=True)
