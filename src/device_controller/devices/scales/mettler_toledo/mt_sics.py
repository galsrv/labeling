from devices.scales.base import BaseScaleDriver
from devices.scales.mettler_toledo.utils import decode_response

get_gross_weight_command = b'S\r\n'
get_immediate_weight_command = b'SI\r\n'
set_tare_command = b'T\r\n'
clear_tare_command = b'TAC\r\n'


class MtSics(BaseScaleDriver):
    """Класс с реализацией протокола MTSics Level 1.

    Проверены весы Mettler Toledo IND226
    Дефолтные параметры: Частота = 9600, бит = 8, стоп бит = 1, четность = нет
    """
    def __init__(self) -> None:
        super().__init__(
            command=get_gross_weight_command,
            decode_response_func=decode_response
        )


weight_service_mt_sics = MtSics()
