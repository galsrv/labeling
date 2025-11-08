from pydantic import BaseModel

from workplaces.models import ScalesDriver

class ScalesReadSchema(BaseModel):
    """Модель чтения записи весов."""
    id: int
    ip: str
    port: int
    driver: ScalesDriver
    description: str

class WorkplaceReadSchema(BaseModel):
    """Модель чтения записи рабочего места."""
    id: int
    description: str
    scales_id: int
    scales: ScalesReadSchema