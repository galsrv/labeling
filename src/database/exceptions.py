class BaseDBException(Exception):
    """Базовый класс исключений при операциях с БД."""


class ObjectNotFound(BaseDBException):
    """Исключение - Объект не найден."""


class ObjectNotModified(BaseDBException):
    """Исключение - Объект не был изменен."""
