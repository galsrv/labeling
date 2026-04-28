from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс настроек приложения."""
    model_config = SettingsConfigDict(env_file='../infra/.env', env_file_encoding='utf-8')

    APP_TITLE: str = 'Labeling Application'

    # Этот блок читаем из .env

    PROD_ENVIRONMENT: bool = False

    JWT_SECRET: str
    JWT_ALGORITM: str = 'HS256'
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRES_DAYS: int = 30
    REFRESH_TOKEN_ENTROPY_SIZE: int = 48
    REFRESH_TOKEN_HASH_LENGTH: int = 255

    BACKEND_HOST: str = '127.0.0.1'
    BACKEND_PORT: int = 8000

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB_HOST: str
    POSTGRES_DB_PORT: str
    POSTGRES_DB: str

    SQL_ECHO: bool = False

    @property
    def DATABASE_URL(self) -> str:  # noqa: D102, N802
        return (
        f'postgresql+asyncpg://'
        f'{self.POSTGRES_USER}:'
        f'{self.POSTGRES_PASSWORD}@'
        f'{self.POSTGRES_DB_HOST}:{self.POSTGRES_DB_PORT}/'
        f'{self.POSTGRES_DB}'
    )

    # Роутинг и логирование

    OPENAPI_URL: str = '/api/openapi.json'
    DOCS_URL: str = '/api/docs'
    REDOC_URL: str = '/api/redoc'

    API_URL_PREFIX: str = '/api/v1'
    HTML_URL_PREFIX: str = '/web'
    WEBSOCKET_URL_PREFIX: str = '/ws'

    STATIC_FILES_URL: str = '/static'
    STATIC_FILES_DIR: str = '../static'

    WEB_TEMPLATE_DIR_PATH: str = '../static/templates'

    LOG_FILE_PATH: str = '../logs/log.txt'
    LOG_NUMBER_OF_FILES_TO_KEEP: int = 5
    LOG_FILE_MAX_SIZE: str = '1 MB'

    # Валидация объектов

    USER_USERNAME_MAX_LENGTH: int = 15
    USER_FIRST_NAME_MAX_LENGTH: int = 15
    USER_LAST_NAME_MAX_LENGTH: int = 15
    USER_PASSWORD_MAX_LENGTH: int = 255
    USER_ROLE_NAME_MAX_LENGTH: int = 15
    USER_PRIVILEGE_NAME_MAX_LENGTH: int = 15

    REFRESH_TOKEN_CLEANUP_JOB_DELAY_SECONDS: int = 5 * 60 * 60  # 5 часов

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

    SGTIN_INSERT_MAX_FILE_SIZE_BYTES: int = 500_000  # 500 KB

    SGTIN_SHELF_LIFE: int = 30

    BATCH_PRINT_MAX_NUMBER_OF_LABELS: int = 1000
    BATCH_PRINT_DELAY: float = 0.3

    # Коммуникация с устройствами

    DEVICE_RESPONSE_SIZE_BYTES: int = 2048

    CONNECT_TO_DEVICE_TIMEOUT: int = 2
    CONNECT_TO_DEVICE_ATTEMPTS: int = 3
    DEVICE_POLL_INTERVAL: float = 0.5

    # Сообщения пользователю и для логов

    MESSAGE_APP_STARTED: str = 'Сервер FastAPI запущен на {host}:{port}'

    MESSAGE_INFO_ENDPOINT_CALL: str = 'Обращение {method}:{url}'
    MESSAGE_ERROR_PROCESSING_REQUEST: str = 'Ошибка обработки запроса к {url}: {error}'

    MESSAGE_DB_OBJECT_GET: str = 'DB SELECT: модель {model}, id {obj_id}'
    MESSAGE_DB_OBJECTS_GET_BY_FIELD: str = 'DB SELECT: модель {model}, критерий {field}={value}, результат {success}'
    MESSAGE_DB_OBJECT_GET_MULTI: str = 'DB SELECT: модель {model}, {number} записей отобрано'
    MESSAGE_DB_OBJECT_CREATE: str = 'DB INSERT: модель {model}, id {obj_id}'
    MESSAGE_DB_OBJECT_CREATE_MULTI: str = 'DB INSERT: модель {model}, {number} записей создано'
    MESSAGE_DB_OBJECT_CREATE_ERROR: str = 'DB INSERT ERROR: модель {model}, ошибка {error}'
    MESSAGE_DB_OBJECT_MODIFICATION_ERROR: str = 'DB CREATE/DELETE ERROR: модель {model}, ошибка {error}'
    MESSAGE_DB_OBJECT_UPDATE: str = 'DB UPDATE: модель {model}, id {obj_id}'
    MESSAGE_DB_OBJECT_UPDATE_MULTI: str = 'DB UPDATE: модель {model}, {number} записей изменено'
    MESSAGE_DB_OBJECT_UPDATE_ERROR: str = 'DB UPDATE ERROR: модель {model}, ошибка {error}'
    MESSAGE_DB_OBJECT_DOESNT_EXIST: str = 'DB NOT FOUND ERROR: модель {model}, id {obj_id}'
    MESSAGE_DB_OBJECT_DELETE: str = 'DB DELETE: модель {model}, id {obj_id}'
    MESSAGE_DB_OBJECT_DELETE_ERROR: str = 'DB DELETE: модель {model}, ошибка {error}'
    MESSAGE_DB_OBJECT_DELETE_MULTI: str = 'DB DELETE: модель {model}, {number} записей удалено'
    MESSAGE_DB_OBJECT_DELETE_ALL: str = 'DB DELETE ALL: модель {model}'

    MESSAGE_METHOD_NOT_IMPLEMENTED: str = 'Метод не реализован для данного драйвера'
    MESSAGE_WRONG_FONT_ID: str = 'Неверно указан код шрифта для принтера'
    MESSAGE_WRONG_FILESIZE: str = 'Некорректный размер файла'
    MESSAGE_WRONG_FILETYPE: str = 'Некорректный тип файла'
    MESSAGE_WRONG_DRIVER_NAME: str = 'Некорретно указан драйвер'

    MESSAGE_COMMAND_SENT_SUCCESS: str = 'Команда успешно отправлена на устройство'
    MESSAGE_COMMAND_SENT_FAIL: str = 'Ошибка отправки команды на устройство'
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

    MESSAGE_WRONG_WORKPLACE: str = 'Некорректно указано рабочее место'

    MESSAGE_AUTHENTICATION_FAILED: str = 'Предоставлены некорректные данные для аутентификации'
    MESSAGE_ACCESS_TOKEN_IS_MISSING: str = 'Не предоставлен токен аутентификации'
    MESSAGE_ACCESS_TOKEN_IS_EXPIRED: str = 'Предоставленный токен аутентификации просрочен'
    MESSAGE_WRONG_ACCESS_TOKEN: str = 'Предоставленный токен аутентификации неверен'
    MESSAGE_REFRESH_TOKEN_NOT_FOUND: str = 'Предоставленный refresh токен не существует'
    MESSAGE_REFRESH_TOKEN_IS_EXPIRED: str = 'Предоставленный refresh токен истек'
    MESSAGE_TOKEN_CLEANUP_TASK_CREATED: str = 'Создана фоновая задача по удалению просроченных токенов аутентификации'


settings = Settings()


templates = Jinja2Templates(directory=settings.WEB_TEMPLATE_DIR_PATH)
