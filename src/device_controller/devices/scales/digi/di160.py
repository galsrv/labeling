from devices.base import BaseDeviceClient
from devices.scales.digi.utils import decode_response


class DigiDi160(BaseDeviceClient):
    """Класс с реализацией обмена с весами DIGI DI160.

    Дефолтные параметры: Частота = 9600, бит = 7, стоп бит = 1, четность = четные
    Возвращают вес в потоке, поэтому команды запроса веса нет
    """
    def __init__(self) -> None:
        super().__init__(None, decode_response)


weight_service_digi_di160 = DigiDi160()
