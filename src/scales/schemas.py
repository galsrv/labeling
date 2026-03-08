from ipaddress import IPv4Address
from typing import Annotated
from pydantic import AfterValidator, BaseModel, ConfigDict, computed_field

from core.config import settings as s
from device_drivers.drivers import scales_drivers
from device_drivers.scales.scales_base import BaseScalesDriver


def driver_name_validator(value: str) -> str:
    """Проверяем указанное имя драйвера."""
    if value not in scales_drivers.keys():
        raise ValueError(s.MESSAGE_WRONG_DRIVER_NAME)

    return value


class ScalesShortSchema(BaseModel):
    """Модель основных полей весов."""
    ip: IPv4Address
    port: int
    driver_name: Annotated[str, AfterValidator(driver_name_validator)]

    model_config = ConfigDict(from_attributes=True,
                              exclude_computed_fields=True,
                              arbitrary_types_allowed=True)

    @computed_field
    @property
    def driver(self) -> BaseScalesDriver:
        """Получаем драйвер весов. Контроль существования возложен на валидатор."""
        return scales_drivers.get(self.driver_name)


class ScalesReadWebSchema(ScalesShortSchema):
    """Модель представления записи весов для вывода в HTML."""
    id: int
    description: str


class ScalesCreateUpdateWebSchema(BaseModel):
    """Модель создания/изменения весов для вывода в API."""
    ip: IPv4Address
    port: int
    description: str
    driver_name: Annotated[str, AfterValidator(driver_name_validator)]

    model_config = ConfigDict(from_attributes=True)
