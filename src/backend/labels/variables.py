from enum import Enum


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


def get_label_variables() -> list[str]:
    """Возвращаем список значений переменных."""
    return [variable.value for variable in LabelVariables]
