from ipaddress import IPv4Address
from pydantic import BaseModel, ConfigDict

from drivers.schemas import DeviceDriversReadSchema, DeviceDriversWebSchema


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


class ScalesCreateUpdateSchema(BaseModel):
    """Модель создания/изменения весов для вывода в API."""
    ip: IPv4Address
    port: int
    description: str
    driver: DeviceDriversReadSchema

    model_config = ConfigDict(from_attributes=True)


class ScalesCreateUpdateWebSchema(BaseModel):
    """Модель создания/изменения весов для вывода в API."""
    ip: IPv4Address
    port: int
    description: str
    driver_id: int

    model_config = ConfigDict(from_attributes=True)


class ScalesShortSchema(BaseModel):
    """Модель основных полей весов."""
    ip: IPv4Address
    port: int
    driver_name: str
