from device_drivers.printers.ezpl.control_codes import get_control_codes


def build_ezpl_label_command(data: str, control_codes: int = 0) -> bytes:
    """Build printer-ready EZPL bytes from a tokenized command string.

    Supported tokens: <CR>, <^>, <~>
    Newlines are converted to <CR>.
    """
    codes = get_control_codes(control_codes)
    cr = bytes([codes["cr_byte"]])
    caret = bytes([codes["caret_byte"]])
    tilde = bytes([codes["tilde_byte"]])
    gs = bytes([codes["gs_byte"]])
    fnc1 = bytes(codes["fnc1_bytes"])

    token_to_bytes: dict[str, bytes] = {
        "<CR>": cr,
        "<^>": caret,
        "<~>": tilde,
        "<GS>": gs,
        "<FNC1>": fnc1,
    }

    # Normalize newlines and <CR> to a single line-break marker
    data = data.replace("\r\n", "\n").replace("\r", "\n")
    data = data.replace("<CR>", "\n")
    # Collapse duplicate line breaks (e.g., <CR> + newline)
    while "\n\n" in data:
        data = data.replace("\n\n", "\n")

    out = bytearray()
    i = 0
    while i < len(data):
        ch = data[i]
        if ch == "\n":
            out.extend(cr)
            i += 1
            continue

        if ch == "<":
            end = data.find(">", i + 1)
            if end != -1:
                token = data[i : end + 1]
                if token in token_to_bytes:
                    out.extend(token_to_bytes[token])
                    i = end + 1
                    continue

        # Default: keep character as UTF-8
        out.extend(ch.encode("utf-8", errors="replace"))
        i += 1

    # Ensure command ends with CR
    if not out.endswith(cr):
        out.extend(cr)

    return bytes(out)
