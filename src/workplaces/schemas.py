from pydantic import BaseModel, ConfigDict

from printers.schemas import PrinterReadSchema
from scales.schemas import ScalesReadSchema


class WorkplaceReadSchema(BaseModel):
    """Модель представления записи рабочего места для вывода в HTML."""
    id: int
    description: str
    scales: ScalesReadSchema | None = None
    printer1: PrinterReadSchema | None = None
    printer2: PrinterReadSchema | None = None

    model_config = ConfigDict(from_attributes=True)
