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


def parse_boolean(value: Any) -> bool:
    text = normalize_text(value).lower()
    return text in {"да", "true", "1", "yes", "y", "истина"}


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

    candidate = text.replace(" ", "")
    candidate = candidate.replace(",", ".")
    if re.fullmatch(r"-?\d+(?:\.\d+)?", candidate):
        return float(candidate)
    return None


def display_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def safe_float_sum(values: list[float | None]) -> float:
    return float(sum(value for value in values if value is not None))

