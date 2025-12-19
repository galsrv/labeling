from __future__ import annotations

import re
from pathlib import Path

from devices.printers.dpl.control_codes import get_control_codes


def build_dpl_ttf_upload_commands(
    ttf_path: str,
    font_ref_id: str,
    module: str = "D",
    control_codes: int = 0,
) -> bytes:
    """Build a DPL command stream to upload a TTF file as a scalable font."""
    codes: dict = get_control_codes(control_codes)

    stx_byte: int = int(codes["stx_byte"])
    cr_byte: int = int(codes["cr_byte"])

    stx: bytes = bytes([stx_byte])
    cr: bytes = bytes([cr_byte])

    font_file = Path(ttf_path)
    font_data: bytes = font_file.read_bytes()
    size_hex: str = f"{len(font_data):08X}"  # 8 hex digits, padded

    # Stored font name must be ASCII-safe
    raw_name: str = font_file.stem
    safe_name: str = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name)[:32] or "FONT"

    # Validate font_ref_id: exactly 2 printable ASCII chars
    if len(font_ref_id) != 2 or any(ord(ch) < 0x21 or ord(ch) > 0x7E for ch in font_ref_id):
        raise ValueError("font_ref_id must be exactly 2 printable ASCII characters (e.g. '55', '5A').")

    # Header format (as you used successfully):
    # <STX> i <module> T <font_ref_id> <name> <CR> <size_hex> + raw .ttf bytes
    header: bytes = (
        stx
        + b"i"
        + module.encode("ascii")
        + b"T"
        + font_ref_id.encode("ascii")
        + safe_name.encode("ascii")
        + cr
        + size_hex.encode("ascii")
    )

    return header + font_data
