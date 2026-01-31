from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageOps

from device_controller.printers.dpl.control_codes import get_control_codes


def convert_raster_to_monochrome_bmp_bytes(
    image_path: str,
    *,
    max_size_px: Tuple[int, int] = (100, 100),
    threshold: int = 128,
    fix_printer_orientation: bool = True,
) -> bytes:
    """Convert PNG/JPEG/etc. to 1-bit monochrome BMP bytes for Datamax DPL.

    Args:
        image_path: Path to a raster image.
        max_size_px: Max (width, height) in pixels; image is downscaled to fit.
        threshold: 0..255. Pixels >= threshold become white, otherwise black.
        fix_printer_orientation: If True, applies a transform to compensate for
            Datamax mirrored + 90° CCW rendering (rotate CW 90 + mirror).

    Returns:
        Bytes of a 1-bit BMP file.
    """
    if not (0 <= threshold <= 255):
        raise ValueError("threshold must be in range 0..255")

    max_width_px, max_height_px = max_size_px
    if max_width_px <= 0 or max_height_px <= 0:
        raise ValueError("max_size_px must contain positive integers")

    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with Image.open(path) as img:
        # Flatten transparency onto white if present
        if img.mode in ("RGBA", "LA") or ("transparency" in img.info):
            rgba = img.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            img = Image.alpha_composite(background, rgba).convert("RGB")
        else:
            img = img.convert("RGB")

        # Downscale early (before thresholding)
        img.thumbnail((max_width_px, max_height_px), Image.LANCZOS)

        if fix_printer_orientation:
            # Cancel printer output: mirror + 90° CCW
            # Pre-transform: rotate CW 90, then mirror
            img = img.rotate(-90, expand=True)   # CW 90
            img = ImageOps.mirror(img)           # horizontal mirror

        gray = img.convert("L")
        mono = gray.point(lambda p: 255 if p >= threshold else 0, mode="1")

        buffer = io.BytesIO()
        mono.save(buffer, format="BMP")
        return buffer.getvalue()


def build_dpl_image_upload_commands(
    image_path: str,
    module: str = "G",
    image_name: Optional[str] = None,
    control_codes: int = 0,
    ascii_hex: bool = False,
    include_soh_disable: bool = True,
    max_size_px: Tuple[int, int] = (100, 100),
    threshold: int = 128,
    fix_printer_orientation: bool = True,
) -> bytes:
    """Build a DPL command stream to upload an image using <STX>I.

    Supported inputs:
      - .bmp (preferred if already 1-bit mono)
      - .pcx (mono)
      - .img (mono)
      - .png/.jpg/.jpeg -> converted to 1-bit BMP internally

    Args:
        image_path: Path to image file.
        module: Memory module designator (default: "G").
        image_name: Optional stored image name (<= 16 chars). Defaults to file stem.
        control_codes: 0=standard, 1=alternate, 2=alternate2.
        ascii_hex: If True, sends data as ASCII hex (b='A' mode). Otherwise raw bytes.
        include_soh_disable: If True and ascii_hex=False, prefixes <SOH>D<CR>.
        max_size_px: Max size for png/jpg/jpeg conversion.
        threshold: Threshold for png/jpg/jpeg conversion.
        fix_printer_orientation: Apply rotate/mirror fix for Datamax output.

    Returns:
        Bytes ready to send to the printer.
    """
    stx_byte, soh_byte, cr_byte, esc_byte, fnc1_bytes, gs_byte = get_control_codes(control_codes).values()

    stx = bytes([stx_byte])
    soh = bytes([soh_byte])
    cr = bytes([cr_byte])

    file_path = Path(image_path)
    if not file_path.is_file():
        raise FileNotFoundError(str(file_path))

    ext = file_path.suffix.lower()

    if ext in (".png", ".jpg", ".jpeg"):
        image_bytes = convert_raster_to_monochrome_bmp_bytes(
            str(file_path),
            max_size_px=max_size_px,
            threshold=threshold,
            fix_printer_orientation=fix_printer_orientation,
        )
        format_designator = "b"  # BMP as received
    elif ext == ".bmp":
        image_bytes = file_path.read_bytes()
        format_designator = "b"
    elif ext == ".pcx":
        image_bytes = file_path.read_bytes()
        format_designator = "p"
    elif ext == ".img":
        image_bytes = file_path.read_bytes()
        format_designator = "i"
    else:
        raise ValueError(
            "Unsupported image format. Use .png/.jpg/.jpeg/.bmp/.pcx/.img "
            "(PNG/JPEG are converted to 1-bit BMP automatically)."
        )

    raw_name = image_name or file_path.stem
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name)[:16] or "IMAGE"

    # <STX>I a [b] f name <CR> data
    data_type_part = b"A" if ascii_hex else b""
    header = (
        stx
        + b"I"
        + module.encode("ascii")
        + data_type_part
        + format_designator.encode("ascii")
        + safe_name.encode("ascii")
        + cr
    )

    prefix = b""
    if include_soh_disable and not ascii_hex:
        prefix = soh + b"D" + cr

    if ascii_hex:
        payload = image_bytes.hex().upper().encode("ascii")
    else:
        payload = image_bytes

    return prefix + header + payload
