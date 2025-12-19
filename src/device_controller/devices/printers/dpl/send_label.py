from devices.printers.dpl.control_codes import get_control_codes


def build_dpl_unicode_label(data: str, control_codes: int = 0) -> bytes:  # noqa: C901
    """Build printer-ready DPL bytes from a tokenized command string.

    The input `data` may contain tokens like <STX>, <SOH>, <ESC>, <CR>, <FNC1>, <GS>.
    - Control codes are substituted according to `control_codes` mode.
    - Text records (where the second character is '9', e.g. 4911...) are converted so that
      the Unicode text portion (after the 2nd P### field) becomes 4-hex-digit code points
      (required for your working UC + u.. method).
    - Non-text lines (e.g. barcodes like 4F11...) are passed through unchanged (ASCII),
      aside from token substitution.

    Args:
        data: Full command stream with tokens (e.g. "<STX>L<CR>4911...<CR>E<CR>").
        control_codes: 0=standard, 1=alternate, 2=alternate2.

    Returns:
        Bytes ready to send to the printer.
    """
    if control_codes not in (0, 1, 2):
        raise ValueError("control_codes must be 0 (standard), 1 (alternate), or 2 (alternate2).")

    stx_byte, soh_byte, cr_byte, esc_byte, fnc1_bytes, gs_byte = get_control_codes(control_codes).values()

    token_to_bytes: dict[str, bytes] = {
        "<STX>": bytes([stx_byte]),
        "<SOH>": bytes([soh_byte]),
        "<ESC>": bytes([esc_byte]),
        "<CR>": b"",  # handled as record separator/terminator, not inline replacement
        "<FNC1>": bytes(fnc1_bytes),
        "<GS>": bytes([gs_byte]),
    }

    def encode_unicode_hex(text: str) -> bytes:
        # 4 hex digits per character (BMP). Works for Cyrillic.
        return "".join(f"{ord(ch):04X}" for ch in text).encode("ascii")

    def substitute_inline_tokens(segment: str) -> bytes:
        # Replace tokens except <CR> (we split by <CR>).
        out = bytearray()
        i = 0
        while i < len(segment):
            if segment[i] == "<":
                end = segment.find(">", i + 1)
                if end != -1:
                    token = segment[i : end + 1]
                    if token in token_to_bytes and token != "<CR>":
                        out.extend(token_to_bytes[token])
                        i = end + 1
                        continue
            # Regular character (must be ASCII for non-text segments/prefixes)
            ch = segment[i]
            code = ord(ch)
            if code > 0x7F:
                # Keep as Unicode in bytes only if the caller later encodes it via encode_unicode_hex.
                # Here we store it as a marker by raising; text handling is done elsewhere.
                raise UnicodeEncodeError("ascii", segment, i, i + 1, "non-ascii in raw segment")
            out.append(code)
            i += 1
        return bytes(out)

    # Split on <CR> tokens (these are explicit record terminators in the input template).
    raw_segments: list[str] = data.split("<CR>")

    output = bytearray()

    for raw in raw_segments:
        if raw == "":
            continue  # ignore empty (e.g., trailing <CR>)

        # Decide if this is a text record based on the raw (tokenized) content:
        # We only consider it a text record if it starts with something like "4911..."
        # i.e., it does NOT start with "<STX>" or other token and has 2nd char == '9'.
        is_text_record = len(raw) >= 2 and raw[0].isdigit() and raw[1] == "9"

        if not is_text_record:
            # Non-text: substitute tokens and require ASCII (after substitution).
            try:
                output.extend(substitute_inline_tokens(raw))
            except UnicodeEncodeError as exc:
                raise ValueError(
                    f"Non-text record contains non-ASCII characters; keep barcodes ASCII-only: {raw!r}"
                ) from exc
            output.append(cr_byte)
            continue

        # Text record: must contain 2 P-fields; text begins after the 2nd P###.
        first_p = raw.find("P")
        second_p = raw.find("P", first_p + 1)
        if first_p == -1 or second_p == -1:
            raise ValueError(f"Text record must contain two P-fields (e.g., P015P009): {raw!r}")

        text_start = second_p + 4  # 'P' + 3 digits
        if text_start > len(raw):
            raise ValueError(f"Second P-field is incomplete: {raw!r}")

        prefix_str = raw[:text_start]
        text_str = raw[text_start:]

        # Prefix may include tokens like <STX> in theory, but your text records shouldn't.
        # Still, we allow token substitution in the prefix and require ASCII after substitution.
        try:
            prefix_bytes = substitute_inline_tokens(prefix_str)
        except UnicodeEncodeError as exc:
            raise ValueError(f"Text record prefix must be ASCII/tokens only: {prefix_str!r}") from exc

        # Text may include Unicode. Also allow <FNC1>/<GS>/<ESC>0 tokens inside text if user insists.
        # We process those tokens into bytes first, then hex-encode *bytes* as code points is not meaningful,
        # so we only support <FNC1>/<GS> inside non-text barcode data. Keep text text-only.
        if "<FNC1>" in text_str or "<GS>" in text_str or "<ESC>" in text_str or "<STX>" in text_str or "<SOH>" in text_str:
            raise ValueError(
                "Text record contains control tokens inside the Unicode text field. "
                "Keep <FNC1>/<GS> for barcode data only."
            )

        output.extend(prefix_bytes)
        output.extend(encode_unicode_hex(text_str))
        output.append(cr_byte)

    return bytes(output)
