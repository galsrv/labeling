from pydantic import BaseModel, ConfigDict

from drivers.models import DriverType


class DeviceDriversReadSchema(BaseModel):
    """Модель представления записи драйверов для вывода в API."""
    id: int
    name: str
    type: DriverType

    model_config = ConfigDict(from_attributes=True)


class DeviceDriversWebSchema(BaseModel):
    """Модель представления записи драйверов для вывода в HTML."""
    id: int
    name: str
    type: DriverType

    model_config = ConfigDict(from_attributes=True)
