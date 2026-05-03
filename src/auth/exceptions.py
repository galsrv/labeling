class BaseAuthError(Exception):
    """Базовый класс исключений модуля Аутентификация."""


class InvalidCredentialsError(BaseAuthError):
    """Неверная пара логин/пароль либо пользователь неактивен."""


class RefreshTokenNotFoundError(BaseAuthError):
    """Рефреш токен не найден или отозван."""


class RefreshTokenExpiredError(BaseAuthError):
    """Рефреш токен истёк."""


class RefreshTokenCreationError(BaseAuthError):
    """Ошибка создания токена."""


class RefreshTokenDeletionError(BaseAuthError):
    """Ошибка удаления токена."""


class NotAuthorizedError(Exception):
    """Ошибка авторизации на выполнение операции."""
