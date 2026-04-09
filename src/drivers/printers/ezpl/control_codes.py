STANDARD_CONTROL_CODES = {
    "cr_byte": 0x0D,
    "tilde_byte": 0x7E,  # '~'
    "caret_byte": 0x5E,  # '^'
    "gs_byte": 0x1D,  # GS
    # Здесь исправил ответ нейросети
    "fnc1_bytes": [0x7E, 0x31],
}


def get_control_codes(cc_id: int = 0) -> dict:
    """Получаем словарь контрольных кодов (EZPL)."""
    return STANDARD_CONTROL_CODES
