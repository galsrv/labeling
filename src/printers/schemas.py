from ipaddress import IPv4Address
from typing import Annotated
from pydantic import AfterValidator, BaseModel, ConfigDict, field_validator

from core.config import settings as s
from device_drivers.drivers import printer_drivers


class PrinterReadWebSchema(BaseModel):
    """Модель представления записи принтеров для вывода в HTML."""
    id: int
    ip: IPv4Address
    port: int
    description: str
    driver_name: str

    model_config = ConfigDict(from_attributes=True)


def driver_name_validator(value: str) -> str:
    """Проверяем указанное имя драйвера."""
    if value not in printer_drivers.keys():
        raise ValueError(s.MESSAGE_WRONG_DRIVER_NAME)

    return value


class PrinterCreateUpdateWebSchema(BaseModel):
    """Модель создания/изменения принтера для вывода в HTML."""
    ip: IPv4Address
    port: int
    driver_name: Annotated[str, AfterValidator(driver_name_validator)]
    description: str

    model_config = ConfigDict(from_attributes=True)


class PrinterShortSchema(BaseModel):
    """Модель основный полей принтера плюс опционально команда на печать."""
    ip: IPv4Address
    port: int
    driver_name: Annotated[str, AfterValidator(driver_name_validator)]
    command: str | None = None


def filename_length(value: str) -> str:
    """Обрезаем длину файла."""
    if len(value) == 0:
        raise ValueError(s.MESSAGE_WRONG_FILETYPE)

    return value[:15]


class PrinterFontSchema(BaseModel):
    """Модель шрифта для принтера."""
    font_id: int
    file_bytes: bytes
    filename: Annotated[str, AfterValidator(filename_length)]
    content_type: str

    @field_validator('font_id', mode='after')
    @classmethod
    def font_id_range_validator(cls, value: int) -> int:
        """Проверяем введенный номер шрифта."""
        if value not in range(11, 100):
            raise ValueError(s.MESSAGE_WRONG_FONT_ID)
        return value

    @field_validator('content_type', mode='after')
    @classmethod
    def content_type_validator(cls, value: str) -> str:
        """Проверяем переданный тип файла."""
        if value not in ('ttf', 'font/ttf', 'application/octet-stream'):
            raise ValueError(s.MESSAGE_WRONG_FILETYPE)
        return value


class PrinterImageSchema(BaseModel):
    """Модель картинки для принтера."""
    file_bytes: bytes
    filename: Annotated[str, AfterValidator(filename_length)]
