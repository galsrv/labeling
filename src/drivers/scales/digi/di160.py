from drivers.scales.digi.utils import decode_response
from drivers.scales.scales_base import BaseScalesDriver
from drivers.utils import read_until_crlf
from drivers.validators import ScalesModes


class DigiDi160(BaseScalesDriver):
    """Класс с реализацией обмена с весами DIGI DI160.

    Дефолтные параметры: Частота = 9600, бит = 7, стоп бит = 1, четность = четные
    Возвращают вес в потоке, поэтому команды запроса веса нет
    """
    def __init__(self) -> None:
        super().__init__()

        self._mode = ScalesModes.push
        self._get_gross_weight_command = None
        self._frame_reader_func = read_until_crlf
        self._decode_response_func = decode_response


weight_service_digi_di160 = DigiDi160()
