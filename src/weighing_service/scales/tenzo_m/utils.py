import random

from core.validators import ScalesWeightResponse


def _crc_step(b_input: int, b_crc: int) -> int:
    """Perform one CRC step according to the protocol's assembler algorithm.

    Equivalent to the original CRCMaker(b_input, b_CRC).
    """
    al = b_input
    ah = b_crc

    for _ in range(8):
        # Rotate AL left through carry
        carry_al = (al >> 7) & 1
        al = ((al << 1) & 0xFF) | carry_al

        # Rotate AH left through carry (using AL's carry)
        carry_ah = (ah >> 7) & 1
        ah = ((ah << 1) & 0xFF) | carry_al

        # If there was carry from AH rotation → XOR with 0x69
        if carry_ah:
            ah ^= 0x69

    return ah & 0xFF


def _compute_crc(data: bytes, as_hex: bool = False) -> str | int:
    """Compute CRC according to the scale's protocol.

    Processes all bytes + one trailing 0x00.
    Returns int by default, or uppercase hex string if as_hex=True.
    """
    crc = 0x00
    for b in data + b'\x00':
        crc = _crc_step(b, crc)

    return f'{crc:02X}' if as_hex else crc


def decode_weight_frame(data: bytes) -> ScalesWeightResponse | None:
    """Разбираем полученный от весов поток.

    Возвращаем кортеж (вес_брутто, флаг стабильного веса, флаг перегруза),
    либо None, если CRC или иные данные некорректны.
    Frame layout:
      0     1   2   3   4   5   6    7   8  9
    [FF][Adr][COP][W0][W1][W2][CON][ CRC ][FF][FF]
    Работает только для ответа с весом. Для ответа другого формата нужна другая функция.
    """
    try:
        # Minimal sanity checks
        if len(data) < 10:
            return None
        if data[0] != 0xFF or data[-2:] != b'\xFF\xFF':
            return None

        # Extract fields
        # core_without_crc = Adr..CON (bytes 1..6 inclusive)
        core_without_crc = data[1:7]   # bytes: Adr, COP, W0, W1, W2, CON
        crc_expected = data[7]

        # Compute CRC for the core and compare with expected CRC byte
        crc_calculated = _compute_crc(core_without_crc)
        if crc_calculated != crc_expected:
            # Optional debug:
            # logger.warning(f"CRC mismatch: expected {crc_expected:02X}, calc {crc_calculated:02X}, frame={data.hex()}")
            return None

        # Now decode weight bytes and CON
        W0, W1, W2, CON = core_without_crc[2], core_without_crc[3], core_without_crc[4], core_without_crc[5]  # noqa: N806

        # Packed BCD little-endian: W2 W1 W0 → 6 digits
        bcd_value = (W2 << 16) | (W1 << 8) | W0
        digits = (
            f"{(bcd_value >> 16) & 0xFF:02X}"
            f"{(bcd_value >> 8) & 0xFF:02X}"
            f"{bcd_value & 0xFF:02X}"
        )
        raw = int(digits)

        # Decode CON byte
        sign = -1 if (CON & 0b10000000) else 1
        decimal_pos = CON & 0b00000111
        stable = bool(CON & 0b00010000)
        overload = bool(CON & 0b00001000)

        weight = sign * (raw / (10 ** decimal_pos))

        return ScalesWeightResponse(weight=weight, stable=stable, overload=overload)

    except Exception:
        return None


def generate_random_weight_response(min_kg: float, max_kg: float) -> bytes:
    """Генерирует случайный ответ весов в диапазоне [min_kg, max_kg].

    Диапазон задаётся в килограммах.
    Возвращает корректный байтовый кадр (frame) с CRC.
    """
    # --- 1️⃣ Случайный вес ---
    decimals = random.choice([2, 3])  # 2 или 3 знака после запятой
    scale = 10 ** decimals
    weight_kg = round(random.uniform(min_kg, max_kg), decimals)

    # --- 2️⃣ Преобразуем в целое число с учётом знаков после запятой ---
    weight_scaled = int(round(weight_kg * scale))
    weight_str = f"{weight_scaled:06d}"

    def to_bcd_pair(two_digits: str) -> int:
        return (int(two_digits[0]) << 4) | int(two_digits[1])

    W0 = to_bcd_pair(weight_str[4:6])  # noqa: N806
    W1 = to_bcd_pair(weight_str[2:4])  # noqa: N806
    W2 = to_bcd_pair(weight_str[0:2])  # noqa: N806

    # --- 3️⃣ Формируем байт CON ---
    sign = 0 if weight_kg >= 0 else 1
    stable = random.choice([0, 1])
    overload = 1 if random.random() < 0.05 else 0
    CON = (sign << 7) | (stable << 4) | (overload << 3) | decimals  # noqa: N806

    # --- 4️⃣ Собираем тело и считаем CRC ---
    Adr = b'\x01'  # noqa: N806
    COP = b'\xC3'  # noqa: N806
    core = Adr + COP + bytes([W0, W1, W2, CON])

    CRC = _compute_crc(core)  # важно: теперь CRC рассчитывается для Adr..CON  # noqa: N806

    # --- 5️⃣ Собираем полный кадр ---
    frame = b'\xFF' + core + bytes([CRC]) + b'\xFF\xFF'  # pyright: ignore[reportArgumentType]
    return frame
