class BaseDatabaseError(Exception):
    """Базовый класс исключений при операциях с БД."""


class ObjectNotFoundError(BaseDatabaseError):
    """Исключение - Объект не найден."""


class ObjectNotModifiedError(BaseDatabaseError):
    """Исключение - Объект не был изменен."""
