import os

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    """Класс настроек приложения."""

    PROD_ENVIRONMENT: bool = os.getenv('PROD', 'False').lower() in ('true', '1')
    APP_TITLE: str = 'Labeling Application'
    HOST: str = os.getenv('BACKEND_HOST', '127.0.0.1')
    PORT: int = int(os.getenv('BACKEND_PORT', 8000))

    DATABASE_URL: str = (
        f'postgresql+asyncpg://'
        f'{os.getenv('POSTGRES_USER')}:'
        f'{os.getenv('POSTGRES_PASSWORD')}@'
        f'{os.getenv('POSTGRES_DB_HOST')}:{os.getenv('POSTGRES_DB_PORT')}/'
        f'{os.getenv('POSTGRES_DB')}'
    )

    OPENAPI_URL: str = '/api/openapi.json'
    DOCS_URL: str = '/api/docs'
    REDOC_URL: str = '/api/redoc'

    API_URL_PREFIX: str = '/api/v1'

    LOG_FILE_PATH: str = 'logs/log.txt'
    LOG_NUMBER_OF_FILES_TO_KEEP: int = 5
    LOG_FILE_MAX_SIZE: str = '1 MB'

    ITEM_NAME_MAX_LENGTH: int = 100
    ITEM_INGRIDIENTS_MAX_LENGTH: int = 255
    ITEM_NUTRITION_MAX_LENGTH: int = 255
    ITEM_GTIN_MIN_VALUE: int = 1_000_000_000_000
    ITEM_GTIN_MAX_VALUE: int = 9_999_999_999_999

    DRIVER_NAME_MAX_LENGTH: int = 20

    DEVICE_PORT_MIN: int = 1024
    DEVICE_PORT_MAX: int = 65535
    DEVICE_DESCRIPTION_MAX_LENGTH: int = 255

    LABEL_TEMPLATE_NAME_MAX_LENGTH: int = 100
    LABEL_TEMPLATE_COMMAND_MAX_LENGTH: int = 100

    PROCESS_NAME_MAX_LENGTH: int = 100

    PRINTER_MAX_FONT_IMAGE_FILE_SIZE_BYTES: int = 500_000  # 500 Kb

    ERROR_MESSAGE_ENTRY_DOESNT_EXIST: str = 'Запрошенная запись не существует'
    MESSAGE_SAVE_DATA_ERROR: str = 'Ошибка сохрания записи. Проверьте введенные данные'
    MESSAGE_METHOD_NOT_IMPLEMENTED: str = 'Метод не реализован для данного драйвера'
    MESSAGE_WRONG_FONT_ID: str = 'Неверно указан код шрифта для принтера'
    MESSAGE_WRONG_FILESIZE: str = 'Некорректный размер файла'
    MESSAGE_WRONG_FILETYPE: str = 'Некорректный тип файла'

    WEB_URL_PREFIX: str = '/web'
    WEB_TEMPLATE_DIR_PATH: str = 'static/templates'

    DEVICE_CONTROLER_URI: str = os.getenv('CONTROLLER_URI', 'ws://127.0.0.1:9000')

    DEVICE_RESPONSE_SIZE_BYTES: int = 2048

    CONNECT_TO_DEVICE_TIMEOUT: int = 3
    CONNECT_TO_DEVICE_ATTEMPTS: int = 5

    MESSAGE_COMMAND_SENT_SUCCESS: str = 'Команда успешно отправлена на устройство'
    MESSAGE_COMMAND_SENT_FAIL: str = 'Ошибка отправки команды на устройство'
    MESSAGE_WRONG_RESPONSE_FORMAT: str = 'Неверный формат ответа от устройства'
    MESSAGE_DEVICE_RESPONSE_TIMEOUT: str = 'Превышен таймаут ожидания ответа от устройства'
    MESSAGE_DRIVER_NOT_FOUND: str = 'Драйвер для данного устройства не найден'
    MESSAGE_CONNECTION_SUCCESSFUL: str = 'Соединение с устройством успешно установлено'
    MESSAGE_CONNECTION_FAILED: str = 'Не удалось установить соединение с устройством'


settings = Settings()


templates = Jinja2Templates(directory=settings.WEB_TEMPLATE_DIR_PATH)
