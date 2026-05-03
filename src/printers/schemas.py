from ipaddress import IPv4Address
from typing import Annotated
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator

from core.config import settings as s
from core.pagination import BasePageSchema
from drivers.drivers import printer_driver_name_validator


class PrinterReadSchema(BaseModel):
    """Модель представления принтера."""
    id: int
    ip: IPv4Address
    port: int
    description: str
    driver_name: str

    model_config = ConfigDict(from_attributes=True)


class PrinterPageSchema(BasePageSchema):
    """Модель выдачи страницы данных."""
    items: list[PrinterReadSchema]


class PrinterCreateUpdateSchema(BaseModel):
    """Модель создания/изменения принтера."""
    ip: IPv4Address
    port: int = Field(ge=s.DEVICE_PORT_MIN, le=s.DEVICE_PORT_MAX)
    description: str
    driver_name: Annotated[str, AfterValidator(printer_driver_name_validator)]


class PrinterShortSchema(BaseModel):
    """Модель короткого представления принтера."""
    ip: IPv4Address
    port: int = Field(ge=s.DEVICE_PORT_MIN, le=s.DEVICE_PORT_MAX)
    driver_name: Annotated[str, AfterValidator(printer_driver_name_validator)]


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
