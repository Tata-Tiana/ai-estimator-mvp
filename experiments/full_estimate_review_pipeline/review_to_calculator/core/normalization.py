"""Small, purely generic Excel-cell-value helpers - no section/business logic here."""

from __future__ import annotations

import re
from typing import Any

_BLANK_STRINGS = {"", "none", "null", "nan"}


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _BLANK_STRINGS
    return False


def normalize_text(value: Any) -> str:
    if is_blank(value):
        return ""
    text = str(value).replace("\xa0", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def cell_text(value: Any) -> str:
    return normalize_text(value)


def parse_number(value: Any) -> float | None:
    if is_blank(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = normalize_text(value)
    if not text:
        return None

    candidate = text.replace(" ", "").replace(",", ".")
    if re.fullmatch(r"-?\d+(?:\.\d+)?", candidate):
        return float(candidate)
    return None
