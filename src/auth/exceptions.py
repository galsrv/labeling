class BaseAuthException(Exception):
    """Базовый класс исключений модуля Аутентификация."""


class InvalidCredentialsError(BaseAuthException):
    """Неверная пара логин/пароль либо пользователь неактивен."""


class RefreshTokenNotFoundError(BaseAuthException):
    """Рефреш токен не найден или отозван."""


class RefreshTokenExpiredError(BaseAuthException):
    """Рефреш токен истёк."""


class RefreshTokenCreationError(BaseAuthException):
    """Ошибка создания токена."""


class RefreshTokenDeletionError(BaseAuthException):
    """Ошибка удаления токена."""
