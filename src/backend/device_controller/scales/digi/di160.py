from device_controller.scales.scales_base import BaseScalesController
from device_controller.scales.digi.utils import decode_response


class DigiDi160(BaseScalesController):
    """Класс с реализацией обмена с весами DIGI DI160.

    Дефолтные параметры: Частота = 9600, бит = 7, стоп бит = 1, четность = четные
    Возвращают вес в потоке, поэтому команды запроса веса нет
    """
    # def __init__(self) -> None:
    #     super().__init__(
    #         command=None,
    #         decode_response_func=decode_response
    #     )


weight_service_digi_di160 = DigiDi160()
