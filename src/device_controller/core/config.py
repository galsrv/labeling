from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Класс настроек проекта."""
    WS_HOST: str = '127.0.0.1'
    WS_PORT: int = 8000

    MIN_WEIGHT: float = 0.1
    GET_WEIGHT_ATTEMPTS: int = 100
    GET_WEIGHT_TIMEOUT: int = 3
    GET_WEIGHT_POLL_INTERVAL: int = 1

    LOG_FILE_PATH: str = 'logs/log.txt'
    LOG_FILE_MAX_SIZE: str = '1 MB'

    ERROR_UNKNOWN_COMMNAD: str = 'Получена неизвестная команда'
    ERROR_DRIVER_NOT_FOUND: str = 'Драйвер для данного модели не найден'
    ERROR_CONNECTION_CLOSED: str = 'Получен пустой ответ, соединение с весами закрыто'
    ERROR_WEIGHT_NOT_RECEIVED: str = 'Вес не получен'
    ERROR_REQUEST_VALIDATION: str = 'Ошибка валидации - неверный запрос'
    ERROR_RESPONSE_VALIDATION: str = 'Ошибка валидации - получен некорректный ответ весов'

    MESSAGE_EXCHANGE_STOPPED: str = 'Обмен остановлен'
    MESSAGE_EXCHANGE_STARTED: str = 'Обмен запущен'

    MESSAGE_DEVICE_BUSY: str = 'Устройство занято'
    MESSAGE_DEVICE_AVAILABLE: str = 'Устройство доступно'


settings = Settings()
