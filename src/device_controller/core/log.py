from enum import Enum

from loguru import logger

from core.config import settings as s


class L(str, Enum):
    """Дополнительные уровни логирования."""
    SCALES = 'SCALES'


# Добавляем сохранение логов в файл
logger.add(s.LOG_FILE_PATH, rotation=s.LOG_FILE_MAX_SIZE)

# Дополнительный уровень логов  для обмена с весами, для визуального выделения
logger.level(L.SCALES, no=15, color='<yellow>')
