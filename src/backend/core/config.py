import os

from dotenv import load_dotenv
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

    SCALES_PORT_MIN: int = 1024
    SCALES_PORT_MAX: int = 65535
    SCALES_DESCRIPTION_MAX_LENGTH: int = 255

    ERROR_MESSAGE_ENTRY_DOESNT_EXIST: str = 'Запрошенная запись не существует'


settings = Settings()
