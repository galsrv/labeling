from validators.base import DeviceTypes
from devices.printers.base import BasePrinterDriver
from devices.printers.dpl.control_codes import get_control_codes
from devices.printers.dpl.utils import decode_response

stx_byte, soh_byte, cr_byte, esc_byte, fnc1_bytes, gs_byte = get_control_codes().values()

PRINT_QUALITY_LABEL = f'{stx_byte}T{cr_byte}'
PRINT_CONFIGURATION_LABEL = f'{stx_byte}Z{cr_byte}'
GET_CONFIGURATION = f'{stx_byte}KC{cr_byte}'
SET_METRIC_MODE = f'{stx_byte}m{cr_byte}'
GET_MEMORY_MODULE_INFO = f'{stx_byte}Wse*{cr_byte}'
SET_STANDARD_CONTROL_CODE_MODE = '~KcCCS|'
SET_ALTERNATE2_CONTROL_CODE_MODE = f'{stx_byte}KcCC2{cr_byte}'
SELECT_FONT_SYMBOL_SET = f'{stx_byte}ySCP{cr_byte}'


class Dpl(BasePrinterDriver):
    """Класс с реализацией DPL команд для принтера."""
    def __init__(self) -> None:
        super().__init__(
            device_type=DeviceTypes.printer,
            command=None,
            decode_response_func=decode_response
        )

    def print_quality_label(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = PRINT_QUALITY_LABEL.encode()
        self.expect_response = False

    def print_configuration_label(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = PRINT_CONFIGURATION_LABEL.encode()
        self.expect_response = False

    def get_configuration(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = GET_CONFIGURATION.encode()
        self.expect_response = True

    def set_metric_mode(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = SET_METRIC_MODE.encode()
        self.expect_response = False

    def get_memory_module_info(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = GET_MEMORY_MODULE_INFO.encode()
        self.expect_response = True

    def set_standard_control_code_mode(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = SET_STANDARD_CONTROL_CODE_MODE.encode()
        self.expect_response = False

    def set_alternate2_control_code_mode(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = SET_ALTERNATE2_CONTROL_CODE_MODE.encode()
        self.expect_response = False

    def select_font_symbol_set(self) -> None:
        """Устанавливаем параметры для выполнения запроса."""
        self.command = SELECT_FONT_SYMBOL_SET.encode()
        self.expect_response = False


printer_service_dpl = Dpl()
