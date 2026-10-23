from drivers.scales.mettler_toledo.utils import decode_response
from drivers.scales.scales_base import BaseScalesDriver
from drivers.utils import read_fixed_length
from drivers.validators import ScalesModes

get_gross_weight_command = b'S\r\n'
get_immediate_weight_command = b'SI\r\n'
set_tare_command = b'T\r\n'
clear_tare_command = b'TAC\r\n'
get_MT_SICS_level_and_version = b'I1\r\n'



class MtSics(BaseScalesDriver):
    """Класс с реализацией протокола MT-SICS.

    METTLER TOLEDO Standard Interface Command Set (MT-SICS) is divided into four levels (0, 1, 2, 3), depending on the functionality of the device.
    This terminal supports parts of levels 0 and 1:
    • MT-SICS level 0 Command set for the simplest device.
    • MT-SICS level 1 Extension of the command set for standard devices.
    • MT-SICS level 2 Extension of the command set by the commands specific for a scale family.
    • MT-SICS level 3 Extension of the command set by commands specific for a certain application of scale family.
    A feature of this interface is that the commands combined in MT-SICS level 0 and 1 are identical for all devices.
    Both the simplest weighing device and a fully expanded weighing workstation can recognize the commands of MT-SICS levels 0 and 1.

    Получение веса есть в уровне 0
    Проверены весы Mettler Toledo IND236
    Параметры МОХА: Baud rate = 9600, Data bits = 8, Stop bits = 1, Parity = None, Flow control = None, FIFO = Enable
    """
    def __init__(self) -> None:
        super().__init__()

        self._mode = ScalesModes.pull
        self._get_gross_weight_command = get_gross_weight_command
        self._frame_reader_func = read_fixed_length
        self._decode_response_func = decode_response


weight_service_mt_sics = MtSics()
