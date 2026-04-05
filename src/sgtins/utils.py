import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s

from items.service import web_items_service


CODE_PARTS_PATTERN = re.compile(r'^01(?P<gtin>\d{14})21(?P<sgtin>.+?)\x1d93(?P<crypto_end>.+)$')


def split_marking_code(code: str) -> tuple[str, str, str]:
    """Split a GS1 marking code into AI 01, 21 and 93 parts."""
    match = CODE_PARTS_PATTERN.fullmatch(code)

    if match is None:
        raise ValueError(f'{s.MESSAGE_WRONG_GTIN_CODE_STRUCTURE} {code!r}')

    return (
        match.group('gtin'),
        match.group('sgtin'),
        match.group('crypto_end'),
    )


def load_marking_codes_from_file(file_data: bytes | str | Path) -> list[tuple[str, str, str]]:
    """Load marking codes from uploaded file content or a local file path.

    Supported inputs:
    - `bytes`: raw uploaded file content
    - `str`: JSON payload itself or a filesystem path
    - `Path`: filesystem path
    """
    payload = _load_payload(file_data)
    codes = payload.get('codes')

    if not isinstance(codes, list):
        raise TypeError(s.MESSAGE_WRONG_GTIN_FILE_CODES_SECTION)

    parsed_codes = [split_marking_code(code) for code in codes]
    _validate_unique_pairs(parsed_codes)
    return parsed_codes


def _load_payload(file_data: bytes | str | Path) -> dict[str, Any]:
    """Convert supported input types into a JSON object."""
    if isinstance(file_data, bytes):
        return json.loads(file_data.decode('utf-8'), strict=False)

    if isinstance(file_data, Path):
        return json.loads(file_data.read_text(encoding='utf-8'), strict=False)

    if isinstance(file_data, str):
        path = Path(file_data)
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'), strict=False)
        return json.loads(file_data, strict=False)

    raise TypeError(s.MESSAGE_WRONG_GTIN_FILE_TYPE)


def _validate_unique_pairs(codes: list[tuple[str, str, str]]) -> None:
    """Validate that `(sgtin, crypto_end)` pairs are unique within one file."""
    seen_pairs: set[tuple[str, str]] = set()

    for _, sgtin, crypto_end in codes:
        pair = (sgtin, crypto_end)
        if pair in seen_pairs:
            raise ValueError(f'{s.MESSAGE_DUPLICATED_PAIR_GTIN_CRYPTO_END} {pair!r}')
        seen_pairs.add(pair)


async def gtins_in_file_validation(input_data: list[tuple[str, str, str]], session: AsyncSession) -> None:
    """Валидация значения GTIN в загруженном файле."""
    gtins_in_file_set = set(int(el[0]) for el in input_data)
    existings_gtins = await web_items_service.get_all_gtins(session)

    for el in gtins_in_file_set:
        if el not in existings_gtins:
            raise ValueError(f'{s.MESSAGE_GTIN_NOT_FOUND} {el}')
