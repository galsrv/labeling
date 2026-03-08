import re
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

INVALID_VAR_MSG = "Некорретная структура переменной"


_VAR_PATTERN = re.compile(r"\{([^{}]+)\}")  # matches { ... } but not nested braces


def _resolve_path(root: Any, path: str) -> tuple[bool, Any]:
    """Resolve dotted attribute/key path on Pydantic models / dict-like objects.

    Returns (found, value).
    """
    cur = root
    for part in path.split("."):
        if cur is None:
            return False, None

        # dict-like
        if isinstance(cur, Mapping):
            if part in cur:
                cur = cur[part]
                continue
            return False, None

        # pydantic / normal objects
        if hasattr(cur, part):
            cur = getattr(cur, part)
            continue

        return False, None

    return True, cur


def _consume_chunk(text: str, max_len: int) -> tuple[str, str]:
    """Take next chunk up to max_len with "space-aware" splitting.

    - Look for the rightmost space within the first max_len chars
    - Cut at that space (space removed)
    - If no space found, cut exactly max_len
    Returns (chunk, remaining)
    """
    if max_len <= 0 or not text:
        return "", text

    if len(text) <= max_len:
        return text, ""

    window = text[:max_len]
    cut = window.rfind(" ")
    if cut > 0:
        chunk = window[:cut]
        remaining = text[cut + 1 :]  # drop the space
        return chunk, remaining

    # no (useful) space found, hard cut
    chunk = window
    remaining = text[max_len:]
    return chunk, remaining


def build_print_command(command_text: str, values: dict[str, BaseModel]) -> str | None:  # noqa: C901
    """Формируем команду на печать, заполняя переменные.

    Исходная строка command_text содержит имена переменных в фигурных скобках, например {items.tare_weight}

    Словарь values:
      ключи - имена таблиц, они же префиксы имен переменных, например 'items'
      значения - значения переменных в виде модели Pydantic, например values['items'].name

    Функция заменяет имена переменных на их значения.

    Некоторые переменные могут иметь ограничения по длине.
    Например ...{items.ingredients:60}...{items.ingredients:50}... означает, что вместо первого вхождения необходимо вставить первые 60 символов значения.
    Вместо второго вхождения - следующие 50 символов. Если значение полностью вставлено, а переменные продолжают встречаться - вставляется пустая строка.

    Деление переменных по длине производится с учетом пробелов. Например, если нужно вставить 60 символов, то в подстроке будет найден самый правый пробел и деление произойдет по нему.
    Фактически будет вставлено, например, 57 символов, пробел будет отсечен, а оставшиеся два символа будут использованы при следующем вхождении переменной.

    Если переменная не найдена в словаре values, то она остается в незамененном виде.

    Если структура {x.y} или {x.y:z} нарушена,
    если структура {x.y:z} применена для числовой переменной или для даты,
      то вставляется значение "Некорретная структура переменной".

    Контрольные коды, например <STX>, не заменяются.

    Если передана пустая строка или переменная иного типа, то возвращается None.
    Если словарь values пуст, возвращается исходная строка.

    Возвращается строка со всеми заменами, которые удалось произвести.

    Что можно добавить: обработку формата дат вида {order.date:DD.MM}
    """
    # Validate inputs
    if not isinstance(command_text, str) or not command_text.strip():
        return None

    if not values:
        return command_text

    # Tracks remaining text for split-in-pieces variables:
    # key: "items.ingredients" -> remaining string not yet consumed
    remaining_by_var: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:  # noqa: C901
        raw_inner = match.group(1).strip()
        original = match.group(0)

        # Validate basic structure: x.y or x.y:z
        if not raw_inner:
            return INVALID_VAR_MSG

        # Split optional length spec
        if ":" in raw_inner:
            var_part, len_part = raw_inner.split(":", 1)
            var_part = var_part.strip()
            len_part = len_part.strip()

            if not var_part or not len_part:
                return INVALID_VAR_MSG

            try:
                max_len = int(len_part)
            except ValueError:
                return INVALID_VAR_MSG
        else:
            var_part = raw_inner
            max_len = None

        # var_part must have at least one dot: x.y
        if "." not in var_part:
            return INVALID_VAR_MSG

        prefix, path = var_part.split(".", 1)
        prefix = prefix.strip()
        path = path.strip()

        if not prefix or not path:
            return INVALID_VAR_MSG

        # If prefix not provided in values -> leave token untouched
        model = values.get(prefix)
        if model is None:
            return original

        found, value = _resolve_path(model, path)
        if not found:
            return original

        # None becomes empty string
        if value is None:
            return ""

        # Length spec rules
        if max_len is not None:
            # Length slicing is only allowed for strings per your spec
            if isinstance(value, (int, float, bool, date, datetime)):
                return INVALID_VAR_MSG
            if not isinstance(value, str):
                # Unknown type: treat as invalid for length slicing
                return INVALID_VAR_MSG

            full_key = f"{prefix}.{path}"
            remaining = remaining_by_var.get(full_key)
            if remaining is None:
                remaining = value

            chunk, rest = _consume_chunk(remaining, max_len)
            remaining_by_var[full_key] = rest
            return chunk

        # No length spec: just stringify (keep it simple & predictable)
        # (If you want custom formatting for date/float here, do it here.)
        return str(value)

    return _VAR_PATTERN.sub(replace, command_text)
