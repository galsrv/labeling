from device_drivers.scales.scales_base import BaseScalesDriver
from device_drivers.scales.tenzo_m.utils import decode_response
from device_drivers.utils import read_fixed_length
from device_drivers.validators import ScalesModes


get_gross_weight_command = b'\xFF\x01\xC3\xE3\xFF\xFF'
get_net_weight_command = b'\xFF\x01\xC2\x8A\xFF\xFF'
set_tare_command = b'\xFF\x01\xC0\x58\xFF\xFF'


class TensoM(BaseScalesDriver):
    """Класс с реализацией протокола Тензо-М.

    Для используемых команд значения CRC заранее рассчитаны.
    """
    def __init__(self) -> None:
        super().__init__()

        self._mode = ScalesModes.pull
        self._get_gross_weight_command = get_gross_weight_command
        self._frame_reader_func = read_fixed_length
        self._decode_response_func = decode_response


weight_service_tenso_m = TensoM()
