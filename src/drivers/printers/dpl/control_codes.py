STANDARD_CONTROL_CODES = {
    'stx_byte': 0x02,
    'soh_byte': 0x01,
    'cr_byte': 0x0D,
    'esc_byte': 0x1B,
    # Тут непонятно - указанное в мануале <ESC>0 в качестве FNC1 не работает. Использовал инфо из Интернет
    'fnc1_bytes': [0x7E, 0x31],
    'gs_byte': 0x1D
}

ALTERNATE_CONTROL_CODES = {
    'stx_byte': 0x7E,  # '~'
    'soh_byte': 0x5E,  # '^'
    'cr_byte': 0x0D,
    'esc_byte': 0x1B,
    'fnc1_bytes': [0x7E, 0x31],
    'gs_byte': 0x1D
}

ALTERNATE2_CONTROL_CODES = {
    'stx_byte': 0x7E,  # '~'
    'soh_byte': 0x5E,  # '^'
    'cr_byte': 0x7C,  # '|'
    'esc_byte': 0x1B,
    'fnc1_bytes': [0x7E, 0x31],
    'gs_byte': 0x1D
}


def get_control_codes(cc_id: int = 0) -> dict:
    """Получаем словарь контрольных кодов."""
    cc_list: list = [STANDARD_CONTROL_CODES, ALTERNATE_CONTROL_CODES, ALTERNATE2_CONTROL_CODES]
    return cc_list[cc_id]
