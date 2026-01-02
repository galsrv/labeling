from ipaddress import IPv4Address
from pydantic import BaseModel, ConfigDict


class DeviceDriversReadSchema(BaseModel):
    """Модель представления записи драйверов для вывода в API."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DeviceDriversWebSchema(BaseModel):
    """Модель представления записи драйверов для вывода в HTML."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ScalesReadSchema(BaseModel):
    """Модель представления записи весов для вывода в API."""
    id: int
    ip: IPv4Address
    port: int
    description: str
    driver: DeviceDriversReadSchema

    model_config = ConfigDict(from_attributes=True)


class ScalesWebSchema(BaseModel):
    """Модель представления записи весов для вывода в HTML."""
    id: int
    ip: IPv4Address
    port: int
    description: str
    driver: DeviceDriversWebSchema

    model_config = ConfigDict(from_attributes=True)


class PrintersReadSchema(ScalesReadSchema):
    """Модель представления записи принтеров для вывода в API."""
    pass


class PrintersWebSchema(ScalesWebSchema):
    """Модель представления записи принтеров для вывода в HTML."""
    pass


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
