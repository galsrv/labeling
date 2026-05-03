from ipaddress import IPv4Address
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from core.config import settings as s
from core.pagination import BasePageSchema
from drivers.drivers import scales_driver_name_validator


class ScalesReadSchema(BaseModel):
    """Модель представления записи весов."""
    id: int
    ip: IPv4Address
    port: int
    description: str
    driver_name: Annotated[str, AfterValidator(scales_driver_name_validator)]

    model_config = ConfigDict(from_attributes=True)


class ScalesPageSchema(BasePageSchema):
    """Модель выдачи страницы данных."""
    items: list[ScalesReadSchema]


class ScalesCreateUpdateSchema(BaseModel):
    """Модель создания/изменения весов."""
    ip: IPv4Address
    port: int = Field(ge=s.DEVICE_PORT_MIN, le=s.DEVICE_PORT_MAX)
    description: str
    driver_name: Annotated[str, AfterValidator(scales_driver_name_validator)]


class ScalesShortSchema(BaseModel):
    """Модель короткого представления весов."""
    ip: IPv4Address
    port: int = Field(ge=s.DEVICE_PORT_MIN, le=s.DEVICE_PORT_MAX)
    driver_name: Annotated[str, AfterValidator(scales_driver_name_validator)]
