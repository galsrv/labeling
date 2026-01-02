import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    """Класс настроек проекта."""
    PROD: bool = os.getenv('PROD', 'False').lower() in ('true', '1')

    WS_HOST: str = '127.0.0.1'
    WS_PORT: int = 8000

    CONNECT_TO_DEVICE_ATTEMPTS: int = 5
    CONNECT_TO_DEVICE_TIMEOUT: int = 3
    WAIT_FOR_DEVICE_RESPONSE_TIMEOUT: int = 2
    DEVICE_RESPONSE_SIZE_BYTES: int = 20

    DEVICE_PORT_MIN: int = 1024
    DEVICE_PORT_MAX: int = 65535

    DEVICE_POLL_INTERVAL: int = 1
    MIN_WEIGHT: float = 0.1

    LOG_FILE_PATH: str = 'logs/log.txt'
    LOG_NUMBER_OF_FILES_TO_KEEP: int = 5
    LOG_FILE_MAX_SIZE: str = '1 MB'

    ERROR_UNKNOWN_COMMNAD: str = 'Получена неизвестная команда'
    ERROR_DRIVER_NOT_FOUND: str = 'Драйвер для данного модели не найден'
    ERROR_CONNECTION_CLOSED: str = 'Получен пустой ответ, соединение с весами закрыто'
    ERROR_WEIGHT_NOT_RECEIVED: str = 'Вес не получен'
    ERROR_REQUEST_VALIDATION: str = 'Ошибка валидации - неверный запрос'
    ERROR_RESPONSE_VALIDATION: str = 'Ошибка валидации - получен некорректный ответ весов'

    MESSAGE_EXCHANGE_STOPPED: str = 'Обмен остановлен'
    MESSAGE_EXCHANGE_STARTED: str = 'Обмен запущен'
    MESSAGE_COMMAND_SENT: str = 'Команда отправлена на устройство'

    MESSAGE_DEVICE_BUSY: str = 'Устройство занято'
    MESSAGE_DEVICE_AVAILABLE: str = 'Устройство доступно'


settings = Settings()
