from core.config import settings as s

from device_drivers.scales.scales_base import BaseScalesDriver
from device_drivers.scales.tenzo_m.utils import decode_response
from device_drivers.validators import ScalesResponse, DeviceResponse, ResponseTypes


get_gross_weight_command = b'\xFF\x01\xC3\xE3\xFF\xFF'
get_net_weight_command = b'\xFF\x01\xC2\x8A\xFF\xFF'
set_tare_command = b'\xFF\x01\xC0\x58\xFF\xFF'


class TensoM(BaseScalesDriver):
    """Класс с реализацией протокола Тензо-М.

    Для используемых команд значения CRC заранее рассчитаны.
    """
    def _get_gross_weight_command(self) -> bytes:
        return get_gross_weight_command

    def _decode_response(self, response_bytes: bytes) -> DeviceResponse:
        """Декодируем ответ весов."""
        response: ScalesResponse | None = decode_response(response_bytes)

        if response is None:
            return DeviceResponse(ok=False, type=ResponseTypes.error, message=s.MESSAGE_ERROR_DECODING_DEVICE_RESPONSE)

        return DeviceResponse(ok=True, type=ResponseTypes.data, data=response)


weight_service_tenso_m = TensoM()
