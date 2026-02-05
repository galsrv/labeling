from device_controller.printers.printers_base import BasePrinterController
from device_controller.printers.dpl.send_label import build_dpl_unicode_label
from device_controller.printers.dpl.upload_font import build_dpl_ttf_upload_commands
from device_controller.printers.dpl.upload_image import build_dpl_image_upload_commands

PRINT_QUALITY_LABEL = '<STX>T<CR>'
PRINT_CONFIGURATION_LABEL = '<STX>Z<CR>'
GET_CONFIGURATION = '<STX>KC<CR>'
SET_METRIC_MODE = '<STX>m<CR>'
GET_MEMORY_MODULE_INFO = '<STX>Wse*<CR>'
SET_STANDARD_CONTROL_CODE_MODE = '~KcCCS|'
SET_ALTERNATE2_CONTROL_CODE_MODE = '<STX>KcCC2<CR>'
SELECT_FONT_SYMBOL_SET = '<STX>ySCP<CR>'


class Dpl(BasePrinterController):
    """Класс с реализацией DPL команд для принтера."""

    # def __init__(self) -> None:
    #     super().__init__(
    #         command=None,
    #     )

    def _encode_command(self, command: str) -> bytes:
        """Формируем команду для отправки на принтер."""
        return build_dpl_unicode_label(command)

    def _encode_load_font(self, font_file_bytes: bytes, filename: str, font_id: int) -> bytes:
        """Формируем команду загрузки шрифта на принтер."""
        return build_dpl_ttf_upload_commands(font_file_bytes, font_id, filename)

    def _encode_load_image(self, image_file_bytes: bytes, filename: str) -> bytes:
        """Формируем команду загрузки картинки на принтер."""
        return build_dpl_image_upload_commands(image_file_bytes, filename)

    def _decode_response(self, response_bytes: bytes) -> str:
        """Обрабатываем ответ принтера."""
        response_str = response_bytes.decode('utf-8', errors='replace')
        response_str = response_str.replace('\r\n', '\n').replace('\r', '\n')
        return response_str

    def _get_default_command(self) -> str:
        """Команда по умолчанию в форме отправки команд."""
        return GET_CONFIGURATION

    def _get_test_connection_command(self) -> str:
        """Команда для тестирования соединения с принтером."""
        return GET_CONFIGURATION

    def _evaluate_test_connection(self, response: str) -> bool:
        """Оценка успеха сетевого соединения."""
        return 'PRINTER INFORMATION' in response


printer_service_dpl = Dpl()
