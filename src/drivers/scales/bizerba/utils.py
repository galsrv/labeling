import re

from drivers.validators import ScalesResponse

_EDP_WEIGHT_PATTERN = re.compile(
    rb"^([+,])(.)([+-]?\s*\d+(?:[.,]\d+)?)\s*([a-zA-Z]+)?$",
)
_IXNET_DIMENSION_VALUE_PATTERN = re.compile(
    rb"^([A-Za-z]+);([+-]?\d+);([+-]?\d+)$",
)


def _parse_edp_line(line: bytes) -> ScalesResponse | None:
    r"""Parse one Bizerba PC/EDP weight line.

    Typical incoming payload:
        b'+)    0,245kg'

    Meaning:
        byte 0 = weight type marker (`+` gross, `,` net)
        byte 1 = status byte
        tail   = space-padded weight string with optional unit
    """
    match = _EDP_WEIGHT_PATTERN.match(line)
    if not match:
        return None

    _weight_type, status_raw, value_str, _unit = match.groups()

    status = status_raw[0] & 0x7F
    stable = bool(status & 0b00000001)

    try:
        weight = float(value_str.replace(b" ", b"").replace(b",", b"."))
    except ValueError:
        return None

    return ScalesResponse(
        weight=weight,
        stable=stable,
    )


def edp_decode_response(data: bytes) -> ScalesResponse | None:
    r"""Parse Bizerba PC/EDP streaming response.
    """
    try:
        line = data.strip()
        if not line:
            return None

        return _parse_edp_line(line)

    except Exception:
        return None


def _strip_ixnet_transport(data: bytes) -> bytes:
    r"""Extract IXData from the optional IXNET transport frame.

    Manual examples show the payload wrapped as:
        <SOH>0<ETX>254<ETX>001<ETX>IXData<CR><LF>

    Some integrations may expose only IXData, so we accept both forms.
    """
    line = data.strip()
    if not line:
        return b""

    if not line.startswith(b"\x01"):
        return line

    payload = line[1:]
    for _ in range(3):
        _, sep, payload = payload.partition(b"\x03")
        if not sep:
            return b""

    return payload


def _parse_ixnet_dimension_value(raw: bytes) -> float | None:
    r"""Parse IXNET values like b'kg;-3;245' -> 0.245."""
    match = _IXNET_DIMENSION_VALUE_PATTERN.match(raw)
    if not match:
        return None

    _unit, exponent_raw, value_raw = match.groups()
    exponent = int(exponent_raw)
    value = int(value_raw)
    return value * (10 ** exponent)


def _parse_ixnet_status(raw: bytes) -> bool | None:
    r"""Parse IXNET GT0A weight status.

    Manual snippet for GT0A:
        digit 2 = no motion
        0 = unstable
        1 = stable
    """
    if len(raw) < 2:
        return None

    if raw[1:2] == b"0":
        return False
    if raw[1:2] == b"1":
        return True
    return None


def ixnet_decode_response(data: bytes) -> ScalesResponse | None:
    r"""Parse Bizerba IXNET weight response.

    Untested implementation based on the manual:
        I?RX01 -> I!LV01|<Subcmd>|LX02
        I?RX02 -> I!LV01|<Subcmd>|LX02

    Expected subcommands in the LV01 block include:
        GT0A = weight status
        GD07 = gross weight
        GD01 = net weight
        GD02 = tare

    We prefer GD07 because the driver uses gross-weight requests.
    """
    try:
        payload = _strip_ixnet_transport(data)
        if not payload:
            return None

        if payload.startswith(b"I!LV00|"):
            return None

        if not payload.startswith(b"I!"):
            return None

        tokens = [token for token in payload.split(b"|") if token]
        if len(tokens) < 2:
            return None

        stable: bool | None = None
        gross_weight: float | None = None
        net_weight: float | None = None

        index = 1
        while index < len(tokens):
            command = tokens[index]

            if command == b"LX02":
                break

            if index + 1 >= len(tokens):
                break

            value = tokens[index + 1]

            if command == b"GT0A":
                stable = _parse_ixnet_status(value)
            elif command == b"GD07":
                gross_weight = _parse_ixnet_dimension_value(value)
            elif command == b"GD01":
                net_weight = _parse_ixnet_dimension_value(value)

            index += 2

        weight = gross_weight if gross_weight is not None else net_weight
        if weight is None:
            return None

        return ScalesResponse(
            weight=weight,
            stable=stable if stable is not None else False,
        )

    except Exception:
        return None
