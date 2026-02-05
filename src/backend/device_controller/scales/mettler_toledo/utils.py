import re

from device_controller.validators import ScalesResponse

_MT_SICS_PATTERN = re.compile(
    rb"^\s*([A-Z]{1,3})\s+([A-Z])\s+([+-]?\s*\d*\.?\d+)\s*([a-zA-Z]+)\s*$"
)
# Examples matched:
# b"S S      2.168 kg"
# b"SI D   -12.345 g"
# b"T I      0.000 kg"


def decode_response(data: bytes) -> ScalesResponse | None:
    """Parse MT-SICS (Mettler-Toledo IND226) weight response.

    Expected format:
        b"S S      2.168 kg"
        b"S D   -12.345 kg"
        b"S I      0.000 kg"

    Returns:
        ScalesWeightResponse(weight=float, stable=bool, overload=bool)
        or None if invalid / unparsable.
    """
    try:
        # Strip CRLF, extract meaningful part
        line = data.strip()
        if not line:
            return None

        m = _MT_SICS_PATTERN.match(line)
        if not m:
            return None

        cmd, status, value_str, unit = m.groups()

        # Cleanup value – remove internal spaces ("  -12.345")
        value = float(value_str.replace(b" ", b""))

        # Status mapping
        status_char = status.decode()

        if status_char == "S":
            stable = True
            overload = False
        elif status_char == "D":
            stable = False
            overload = False
        elif status_char == "I":  # overload/underload
            stable = False
            overload = True
        else:
            return None  # Unknown status → treat as invalid frame

        return ScalesResponse(
            weight=value,
            stable=stable,
            overload=overload
        )

    except Exception:
        return None
