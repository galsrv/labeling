import os

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
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
    WEB_URL_PREFIX: str = '/web'

    WEB_TEMPLATE_DIR_PATH: str = '../static/templates'

    LOG_FILE_PATH: str = '../logs/log.txt'
    LOG_NUMBER_OF_FILES_TO_KEEP: int = 5
    LOG_FILE_MAX_SIZE: str = '1 MB'

    # Валидация объектов

    ITEM_NAME_MAX_LENGTH: int = 100
    ITEM_INGRIDIENTS_MAX_LENGTH: int = 255
    ITEM_NUTRITION_MAX_LENGTH: int = 255
    ITEM_GTIN_MIN_VALUE: int = 1_000_000_000_000  # 13 digits
    ITEM_GTIN_MAX_VALUE: int = 99_999_999_999_999  # 14 digits

    ORDER_PRODUCTION_DATE_DEPTH_BACK: int = 1
    ORDER_PRODUCTION_DATE_DEPTH_FORWARD: int = 30

    DEVICE_PORT_MIN: int = 1024
    DEVICE_PORT_MAX: int = 65535
    DEVICE_DESCRIPTION_MAX_LENGTH: int = 255

    DRIVER_NAME_MAX_LENGTH: int = 30

    LABEL_TEMPLATE_NAME_MAX_LENGTH: int = 100
    LABEL_TEMPLATE_COMMAND_MAX_LENGTH: int = 100

    PROCESS_NAME_MAX_LENGTH: int = 100

    PRINTER_MAX_FONT_IMAGE_FILE_SIZE_BYTES: int = 500_000  # 500 KB

    GTIN_LENGTH: int = 14
    SGTIN_LENGTH: int = 6
    CRYPTO_END_LENGTH: int = 4

    SGTIN_INSERT_MAX_FILE_SIZE_BYTES: int = 100_000  # 100 KB

    SGTIN_SHELF_LIFE: int = 30

    BATCH_PRINT_MAX_NUMBER_OF_LABELS: int = 1000
    BATCH_PRINT_DELAY: float = 0.3

    # Коммуникация с устройствами

    DEVICE_RESPONSE_SIZE_BYTES: int = 2048

    CONNECT_TO_DEVICE_TIMEOUT: int = 2
    CONNECT_TO_DEVICE_ATTEMPTS: int = 3
    DEVICE_POLL_INTERVAL: float = 0.5
    # WAIT_FOR_DEVICE_RESPONSE_TIMEOUT: int = 2

    # Сообщения пользователю

    MESSAGE_ENTRY_DOESNT_EXIST: str = 'Запрошенная запись не существует'
    MESSAGE_SAVE_DATA_ERROR: str = 'Ошибка сохрания записи. Проверьте введенные данные'
    MESSAGE_METHOD_NOT_IMPLEMENTED: str = 'Метод не реализован для данного драйвера'
    MESSAGE_WRONG_FONT_ID: str = 'Неверно указан код шрифта для принтера'
    MESSAGE_WRONG_FILESIZE: str = 'Некорректный размер файла'
    MESSAGE_WRONG_FILETYPE: str = 'Некорректный тип файла'
    MESSAGE_WRONG_DRIVER_NAME: str = 'Некорретно указан драйвер'

    MESSAGE_COMMAND_SENT_SUCCESS: str = 'Команда успешно отправлена на устройство'
    MESSAGE_COMMAND_SENT_FAIL: str = 'Ошибка отправки команды на устройство'
    MESSAGE_WRONG_RESPONSE_FORMAT: str = 'Неверный формат ответа от устройства'
    MESSAGE_DEVICE_RESPONSE_TIMEOUT: str = 'Превышен таймаут ожидания ответа от устройства'
    MESSAGE_DRIVER_NOT_FOUND: str = 'Драйвер для данного устройства не найден'
    MESSAGE_CONNECTION_SUCCESSFUL: str = 'Соединение с устройством успешно установлено'
    MESSAGE_CONNECTION_FAILED: str = 'Не удалось установить соединение с устройством'
    MESSAGE_ERROR_DECODING_DEVICE_RESPONSE: str = 'Не удалось преобразовать ответ устройства'
    MESSAGE_ERROR_LABEL_PRINTING: str = 'Ошибка печати этикетки'

    MESSAGE_WRONG_GTIN_CODE_STRUCTURE: str = 'Неверный формат кода маркировки:'
    MESSAGE_WRONG_GTIN_FILE_CODES_SECTION: str = 'Секция `codes` должна являться списком'
    MESSAGE_WRONG_GTIN_FILE_TYPE: str = 'Неподдерживаемый тип файла'
    MESSAGE_DUPLICATED_PAIR_GTIN_CRYPTO_END: str = 'Обнаружен дубль пары серийный номер + крипто-хвост:'
    MESSAGE_GTIN_NOT_FOUND: str = 'В файле обнаружен GTIN, не принадлежащий ни одному продукту в системе:'
    MESSAGE_ERROR_LOADING_SGTIN_FILE: str = 'Ошибка загрузки файла с кодами маркировки'
    MESSAGE_SUCCESSFUL_FILE_PROCESSING: str = 'Файл с кодами маркировки успешно обработан'

    MESSAGE_WRONG_AMOUNT_BATCH_LABEL_PRINT: str = 'Количество этикеток для печати должно быть в диапазоне от 1 до 1000'
    MESSAGE_NOT_ENOUGH_CODES_TO_PRINT: str = 'Недостаточно кодов маркировки для печати:'
    MESSAGE_NUMBER_OF_LABELS_PRINTED: str = 'Напечатано этикеток:'

    MESSAGE_ORDER_WRONG_PRODUCTION_DATE: str = 'Некорректная дата производства'


settings = Settings()


templates = Jinja2Templates(directory=settings.WEB_TEMPLATE_DIR_PATH)
