from devices.base import BaseDeviceDriver
from devices.scales.tenzo_m.utils import decode_response

get_gross_weight_command = b'\xFF\x01\xC3\xE3\xFF\xFF'
get_net_weight_command = b'\xFF\x01\xC2\x8A\xFF\xFF'
set_tare_command = b'\xFF\x01\xC0\x58\xFF\xFF'


class TensoM(BaseDeviceDriver):
    """Класс с реализацией протокола Тензо-М.

    Для используемых команд значения CRC заранее рассчитаны.
    """
    def __init__(self) -> None:
        super().__init__(get_gross_weight_command, decode_response)


weight_service_tenso_m = TensoM()
