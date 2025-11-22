from ipaddress import IPv4Address
from pydantic import BaseModel


class DeviceDriversReadSchema(BaseModel):
    """Модель чтения записи драйверов."""
    id: int
    name: str


class ScalesReadSchema(BaseModel):
    """Модель чтения записи весов."""
    id: int
    ip: IPv4Address
    port: int
    description: str
    driver: DeviceDriversReadSchema


class WorkplaceReadSchema(BaseModel):
    """Модель чтения записи рабочего места."""
    id: int
    description: str
    scales: ScalesReadSchema
