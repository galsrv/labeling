from pydantic import BaseModel, ConfigDict


class LabelTemplatesReadWebSchema(BaseModel):
    """Модель представления шаблона этикетки для вывода в HTML."""
    id: int
    name: str
    driver_name: str
    print_command: str

    model_config = ConfigDict(from_attributes=True)


class LabelTemplatesCreateUpdateWebSchema(BaseModel):
    """Модель изменения шаблона этикетки для вывода в HTML."""
    name: str
    driver_name: str
    print_command: str


class PrintLabelTestPayload(BaseModel):
    """Модель запроса на печать тестовой этикетки."""
    print_command: str
    item_id: int
    printer_id: int
    driver_name: str
