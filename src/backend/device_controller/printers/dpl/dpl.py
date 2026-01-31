from device_controller.printers.printers_base import BasePrinterDriver
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


class Dpl(BasePrinterDriver):
    """Класс с реализацией DPL команд для принтера."""

    # def __init__(self) -> None:
    #     super().__init__(
    #         command=None,
    #     )

    def _encode_command_func(self, command: str) -> bytes:
        return build_dpl_unicode_label(command)

    def _encode_load_font_func(self, font_file_bytes: bytes, filename: str, font_id: int) -> bytes:
        return build_dpl_ttf_upload_commands(font_file_bytes, font_id, filename)

    def _encode_load_image_func(self, image_file_bytes: bytes, filename: str) -> bytes:
        return build_dpl_image_upload_commands(image_file_bytes, image_name=filename)


printer_service_dpl = Dpl()
