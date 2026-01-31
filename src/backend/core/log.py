from enum import Enum
from loguru import logger

from core.config import settings as s


class L(str, Enum):
    """Дополнительные уровни логирования."""
    DEVICES = 'DEVICES'


# Добавляем сохранение логов в файл
logger.add(
    sink=s.LOG_FILE_PATH,
    rotation=s.LOG_FILE_MAX_SIZE,
    retention=s.LOG_NUMBER_OF_FILES_TO_KEEP
)

# Дополнительный уровень логов  для обмена с оборудованием, для визуального выделения
logger.level('DEVICES', no=15, color='<yellow>')
