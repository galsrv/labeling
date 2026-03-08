import re

from device_drivers.printers.ezpl.control_codes import get_control_codes


def _to_font_slot(font_id: int | str) -> str:
    """Convert numeric or string font_id to EZPL slot letter A-Z."""
    if isinstance(font_id, int):
        if 1 <= font_id <= 26:
            return chr(ord("A") + font_id - 1)
        if 65 <= font_id <= 90:
            return chr(font_id)
    else:
        font_id_str = str(font_id).strip()
        if len(font_id_str) == 1 and font_id_str.isalpha():
            return font_id_str.upper()

    raise ValueError("font_id must map to A-Z (1-26 or 'A'-'Z').")


def build_ezpl_ttf_upload_commands(
    font_bytes: bytes,
    font_id: int | str,
    filename: str,
    control_codes: int = 0,
) -> bytes:
    """Build EZPL command stream to download a TrueType font.

    Syntax: ~H,TTF,Xname,size<CR>data
      X = A..Z (font slot)
      name = font name (alnum)
      size = size of font file in bytes
      data = binary TTF data
    """
    codes = get_control_codes(control_codes)
    cr = bytes([codes["cr_byte"]])
    tilde = bytes([codes["tilde_byte"]])

    slot = _to_font_slot(font_id)
    raw_name = filename.rsplit(".", 1)[0]
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", raw_name)[:16] or "FONT"
    size = str(len(font_bytes)).encode("ascii")

    header = (
        tilde
        + b"H,TTF,"
        + slot.encode("ascii")
        + safe_name.encode("ascii")
        + b","
        + size
        + cr
    )

    return header + font_bytes
