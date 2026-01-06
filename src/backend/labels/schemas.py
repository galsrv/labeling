from pydantic import BaseModel, ConfigDict

from workplaces.schemas import DeviceDriversWebSchema


class LabelTemplatesWebSchema(BaseModel):
    """Модель представления шаблона этикетки для вывода в HTML."""
    id: int
    name: str
    driver: DeviceDriversWebSchema
    print_command: str

    model_config = ConfigDict(from_attributes=True)


class LabelTemplatesCreateUpdateWebSchema(BaseModel):
    """Модель изменения шаблона этикетки для вывода в HTML."""
    name: str
    driver_id: int
    print_command: str
