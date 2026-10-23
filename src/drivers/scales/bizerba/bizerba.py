from drivers.scales.bizerba.utils import edp_decode_response, ixnet_decode_response
from drivers.scales.scales_base import BaseScalesDriver
from drivers.utils import read_until_crlf
from drivers.validators import ScalesModes

# Команды для IXNET, для EDP команды не нужны
get_weight_with_stable_check = b'\x010\x03254\x03001\x03I?LV01|RX02|LX02\r\n'


class BizerbaEdp(BaseScalesDriver):
    """Класс с реализацией протокола Bizerba PC/EDP.

    Протокол активируется на терминале как step 70 = 20

    Весы возвращают вес в потоке каждые 200 мс. Фрагмент заканчивается символами <CR><LF>

    Проверены весы Bizerba is20
    """
    def __init__(self) -> None:
        super().__init__()

        self._mode = ScalesModes.push
        self._get_gross_weight_command = None
        self._frame_reader_func = read_until_crlf
        self._decode_response_func = edp_decode_response


class BizerbaIxnet(BaseScalesDriver):
    """Класс с реализацией протокола Bizerba IXNET.

    Протокол активируется на терминале как step 70 = 24

    Протокол более комплексный. 
    Работает в режиме вопрос/ответ.

    Не тестировалось
    """
    def __init__(self) -> None:
        super().__init__()

        self._mode = ScalesModes.pull
        self._get_gross_weight_command = get_weight_with_stable_check
        self._frame_reader_func = read_until_crlf
        self._decode_response_func = ixnet_decode_response


weight_service_bizerba_edp = BizerbaEdp()

weight_service_bizerba_ixnet = BizerbaIxnet()