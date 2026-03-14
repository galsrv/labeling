from device_drivers.scales.scales_base import BaseScalesDriver
from device_drivers.scales.mettler_toledo.utils import decode_response
from device_drivers.utils import read_fixed_length
from device_drivers.validators import ScalesModes

get_gross_weight_command = b'S\r\n'
get_immediate_weight_command = b'SI\r\n'
set_tare_command = b'T\r\n'
clear_tare_command = b'TAC\r\n'


class MtSics(BaseScalesDriver):
    """Класс с реализацией протокола MTSics Level 1.

    Проверены весы Mettler Toledo IND226
    Дефолтные параметры: Частота = 9600, бит = 8, стоп бит = 1, четность = нет
    """
    def __init__(self) -> None:
        super().__init__()

        self._mode = ScalesModes.pull
        self._get_gross_weight_command = get_gross_weight_command
        self._frame_reader_func = read_fixed_length
        self._decode_response_func = decode_response


weight_service_mt_sics = MtSics()
