from __future__ import annotations

import sys
from pathlib import Path


EXPERIMENT_DIR = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "earthworks_parser_google_stage1"
)
sys.path.insert(0, str(EXPERIMENT_DIR))

from pricing.google_price_registry_reader import parse_price  # noqa: E402


def test_parse_price_preserves_numeric_registry_values() -> None:
    assert parse_price(3500) == 3500.0
    assert parse_price("3 500") == 3500.0
    assert parse_price("3\u00a0500,25") == 3500.25


def test_parse_price_rejects_empty_and_invalid_values() -> None:
    assert parse_price(None) is None
    assert parse_price("") is None
    assert parse_price("not-a-price") is None
