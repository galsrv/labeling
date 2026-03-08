from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Optional

from PIL import Image

from device_drivers.printers.ezpl.control_codes import get_control_codes


def _convert_jpeg_to_mono_png(image_bytes: bytes) -> bytes:
    """Convert JPEG bytes to 1-bit monochrome PNG bytes."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("L")
        mono = img.point(lambda p: 255 if p >= 128 else 0, mode="1")
        buf = io.BytesIO()
        mono.save(buf, format="PNG")
        return buf.getvalue()


def build_ezpl_image_upload_commands(
    image_bytes: bytes,
    filename: str | None,
    image_name: Optional[str] = None,
    control_codes: int = 0,
) -> bytes:
    """Build EZPL command stream to download an image to printer memory.

    Syntax: ~En,name,size<CR>data
      n = P (PCX), B (BMP), N (PNG)
      name = image name (<= 20 chars)
      size = size of image data in bytes
    """
    codes = get_control_codes(control_codes)
    cr = bytes([codes["cr_byte"]])
    tilde = bytes([codes["tilde_byte"]])

    if not filename:
        raise ValueError("filename is required to determine image type")

    ext = Path(filename).suffix.lower()
    if ext in (".jpg", ".jpeg"):
        image_bytes = _convert_jpeg_to_mono_png(image_bytes)
        type_char = "N"
    elif ext == ".pcx":
        type_char = "P"
    elif ext == ".bmp":
        type_char = "B"
    elif ext == ".png":
        type_char = "N"
    else:
        raise ValueError("Unsupported image format. Use .pcx/.bmp/.png/.jpg/.jpeg")

    raw_name = image_name or Path(filename).stem
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", raw_name)[:20] or "IMAGE"
    size = str(len(image_bytes)).encode("ascii")

    header = (
        tilde
        + b"E"
        + type_char.encode("ascii")
        + b","
        + safe_name.encode("ascii")
        + b","
        + size
        + cr
    )

    return header + image_bytes
