from device_drivers.printers.printers_base import BasePrinterDriver
from device_drivers.printers.ezpl.send_label import build_ezpl_label_command
from device_drivers.printers.ezpl.upload_font import build_ezpl_ttf_upload_commands
from device_drivers.printers.ezpl.upload_image import build_ezpl_image_upload_commands

GET_CONFIGURATION = '^XGET,CONFIG'


class Ezpl(BasePrinterDriver):
    """Класс с реализацией EZPL команд для принтера."""

    def _get_default_command(self) -> str:
        """Команда по умолчанию в форме отправки команд."""
        return GET_CONFIGURATION

    def _encode_command(self, command: str) -> bytes:
        """Формируем команду для отправки на принтер."""
        return build_ezpl_label_command(command)

    def _encode_load_font(self, font_file_bytes: bytes, filename: str, font_id: int) -> bytes:
        """Формируем команду загрузки шрифта на принтер."""
        return build_ezpl_ttf_upload_commands(font_file_bytes, font_id, filename)

    def _encode_load_image(self, image_file_bytes: bytes, filename: str) -> bytes:
        """Формируем команду загрузки картинки на принтер."""
        return build_ezpl_image_upload_commands(image_file_bytes, filename)

    def _get_test_connection_command(self) -> str:
        """Команда для тестирования соединения с принтером."""
        return GET_CONFIGURATION

    def _evaluate_test_connection(self, response: str) -> bool:
        """Оценка успеха сетевого соединения."""
        return 'X' in response


printer_ezpl_driver = Ezpl()
