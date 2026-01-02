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

    ERROR_MESSAGE_ENTRY_DOESNT_EXIST: str = 'Запрошенная запись не существует'

    WEB_URL_PREFIX: str = '/web'
    WEB_TEMPLATE_DIR_PATH: str = 'static/templates'


settings = Settings()


templates = Jinja2Templates(directory=settings.WEB_TEMPLATE_DIR_PATH)
