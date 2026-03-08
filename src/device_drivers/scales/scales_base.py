from device_drivers.base import BaseDeviceDriver
from device_drivers.validators import DeviceResponse, ScalesResponse, ResponseTypes


class BaseScalesDriver(BaseDeviceDriver):
    """Базовый класс драйверов весов."""

    async def get_weight(self, host: str, port: int) -> ScalesResponse:
        """Получаем вес с весов однократно."""
        command_bytes: bytes | None = self._get_gross_weight_command()

        if command_bytes is None:
            pass  # Написать когда буду работать с весами без стартовой команды

        try:
            response_bytes: bytes = await self._send_and_receive_workflow(host, port, command_bytes)
            response: DeviceResponse = self._decode_response(response_bytes)
            return response

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.error, message=str(e))
