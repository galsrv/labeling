from __future__ import annotations

import re
from device_controller.printers.dpl.control_codes import get_control_codes


def build_dpl_ttf_upload_commands(
    ttf_bytes: bytes,
    font_ref_id: int | str,
    filename: str,
    module: str = "D",
    control_codes: int = 0,
) -> bytes:
    """Build a DPL command stream to upload a TTF file as a scalable font."""
    codes: dict = get_control_codes(control_codes)

    stx_byte: int = int(codes["stx_byte"])
    cr_byte: int = int(codes["cr_byte"])

    stx: bytes = bytes([stx_byte])
    cr: bytes = bytes([cr_byte])

    font_data: bytes = ttf_bytes
    size_hex: str = f"{len(font_data):08X}"  # 8 hex digits, padded

    # Stored font name must be ASCII-safe
    raw_name: str = filename.rsplit(".", 1)[0]
    safe_name: str = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name)[:32] or "FONT"

    # Validate font_ref_id: exactly 2 printable ASCII chars
    if isinstance(font_ref_id, int):
        font_id_num = font_ref_id
        font_ref_id_str = f"{font_id_num:02d}"
    else:
        font_ref_id_str = str(font_ref_id)
        font_id_num = int(font_ref_id_str) if font_ref_id_str.isdigit() else -1

    if len(font_ref_id_str) != 2 or not font_ref_id_str.isdigit() or not (11 <= font_id_num <= 99):
        raise ValueError("font_ref_id must be two digits in the range 11-99.")

    # Header format (as you used successfully):
    # <STX> i <module> T <font_ref_id> <name> <CR> <size_hex> + raw .ttf bytes
    header: bytes = (
        stx
        + b"i"
        + module.encode("ascii")
        + b"T"
        + font_ref_id_str.encode("ascii")
        + safe_name.encode("ascii")
        + cr
        + size_hex.encode("ascii")
    )

    return header + font_data
