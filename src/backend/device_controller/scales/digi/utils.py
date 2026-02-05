from device_controller.validators import ScalesResponse


def decode_response(data: bytes) -> ScalesResponse | None:
    r"""Parse DIGI DI-160 ASCII streaming frame.

    Typical incoming payload:
        b'000.745\r000.000\r\n'

    Meaning:
        line1 = gross weight (string-formatted float)
        line2 = always zero, can be ignored

    Returns:
        ScalesWeightResponse(weight=float, stable=False, overload=False)
        or None if parsing fails.
    """
    try:
        # Split into lines (keep only non-empty)
        lines = [ln for ln in data.split(b"\r") if ln.strip()]
        if not lines:
            return None

        # First non-empty line contains the weight reading
        first = lines[0].strip()

        # Must look like digits.dot.digits, e.g. b"000.745"
        try:
            weight = float(first)
        except Exception:
            return None

        # DI-160 streaming does not provide stable/overload flags
        stable = True
        overload = False

        return ScalesResponse(
            weight=weight,
            stable=stable,
            overload=overload,
        )

    except Exception:
        return None
