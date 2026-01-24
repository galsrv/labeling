from enum import Enum
from typing import Type

from sqlalchemy.inspection import inspect

from core.database import TOrm
from items.models import ItemsOrm


class ControlCodes(Enum):
    """Контрольные коды для вставки в команду печати."""
    STX = '<STX>'
    SOH = '<SOH>'
    ESC = '<ESC>'
    CR = '<CR>'
    FNC1 = '<FNC1>'
    GS = '<GS>'


class LabelVariables(Enum):
    """Переменные, используемые при печати этикетки."""
    item_name = '{item_name}'
    ingredients = '{ingredients}'
    nutrition = '{nutrition}'
    nominal_weight = '{nominal_weight}'
    gtin = '{gtin}'
    shelf_life = '{shelf_life}'


def get_control_codes() -> list[str]:
    """Возвращаем список значений контрольных кодов."""
    return [code.value for code in ControlCodes]


def __get_column_names(model: Type[TOrm]) -> list[str]:
    """Возвращаем список имен полей модели."""
    return [f'{{{model.__tablename__}.{column.key}}}' for column in inspect(model).mapper.column_attrs]


def get_label_variables() -> list[str]:
    """Возвращаем список значений переменных."""
    items_variables = __get_column_names(ItemsOrm)
    return items_variables
