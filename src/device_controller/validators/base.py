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
