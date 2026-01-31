from enum import Enum


class DeviceTypes(Enum):
    """Енум-класс для типов устройств."""
    printer = 'printer'
    scales = 'scales'


class Modes(Enum):
    """Енум-класс для режимов, в которых работает веб-сервер."""
    send = 'send'
    stream = 'stream'
    get = 'get'
    stop = 'stop'
    status = 'status'


class SendMode():
    """Класс режима отправки команд без получения ответа."""
    sending_request = True
    awaiting_response = False


class StreamMode():
    """Класс режима отправки команд без получения ответа."""
    sending_request = True
    awaiting_response = False
