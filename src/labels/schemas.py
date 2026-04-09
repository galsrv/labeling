from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict

from drivers.drivers import printer_driver_name_validator


class LabelTemplatesReadSchema(BaseModel):
    """Модель представления шаблона этикетки."""
    id: int
    name: str
    driver_name: str
    print_command: str

    model_config = ConfigDict(from_attributes=True)


class LabelTemplatesCreateUpdateSchema(BaseModel):
    """Модель создания/изменения шаблона этикетки."""
    name: str
    driver_name: Annotated[str, AfterValidator(printer_driver_name_validator)]
    print_command: str


class PrintLabelTestPayload(BaseModel):
    """Модель запроса на печать тестовой этикетки."""
    print_command: str
    item_id: int
    printer_id: int
    driver_name: Annotated[str, AfterValidator(printer_driver_name_validator)]
