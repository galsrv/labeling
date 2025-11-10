from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WS_HOST: str = '127.0.0.1'
    WS_PORT: int = 8000

    MIN_WEIGHT: float = 0.1
    GET_WEIGHT_ATTEMPTS: int = 100
    GET_WEIGHT_TIMEOUT: int = 3
    GET_WEIGHT_POLL_INTERVAL: int = 1

    ERROR_DRIVER_NOT_FOUND: str = 'Драйвер для данного модели не найден'
    ERROR_WEIGHT_NOT_RECEIVED: str = 'Вес не получен'
    ERROR_REQUEST_VALIDATION: str = 'Ошибка валидации - неверный запрос'
    ERROR_RESPONSE_VALIDATION: str = 'Ошибка валидации - получен некорректный ответ весов'

    MESSAGE_EXCHANGE_STOPPED: str = 'Обмен остановлен'

settings = Settings()
