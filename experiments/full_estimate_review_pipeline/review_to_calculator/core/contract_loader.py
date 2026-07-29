"""Reads section_contract.yaml - the ground truth for what a section's calculator input
requires. Read the contract, not the calculator source, when deciding what the adapter
must fill; the contract has already been cross-checked against the calculator directly.

See ../ADAPTER_BUILD_PLAN.md for the overall adapter architecture this module is part of.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
SECTIONS_DIR = REPO_ROOT / "experiments" / "full_estimate_review_pipeline" / "sections"

REQUIRED_TOP_LEVEL_KEYS = (
    "section",
    "review_parameters",
    "price_keys",
    "defaults",
    "estimate_lines",
    "checks",
)


class ContractError(ValueError):
    pass


def contract_path(section_code: str) -> Path:
    return SECTIONS_DIR / section_code / "section_contract.yaml"


def load_contract(section_code: str) -> dict[str, Any]:
    path = contract_path(section_code)
    if not path.exists():
        raise ContractError(f"No section_contract.yaml for section '{section_code}' at {path}")
    contract = yaml.safe_load(path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in contract]
    if missing:
        raise ContractError(f"{section_code}: contract is missing required top-level keys: {missing}")
    if contract["section"].get("code") != section_code:
        raise ContractError(
            f"{section_code}: contract's section.code is {contract['section'].get('code')!r}, "
            f"expected {section_code!r}"
        )
    return contract


def section_code(contract: dict[str, Any]) -> str:
    return contract["section"]["code"]


def section_name(contract: dict[str, Any]) -> str:
    return contract["section"]["name_ru"]


def calculator_module_path(contract: dict[str, Any]) -> str:
    return contract["section"]["calculator_module"]


def all_review_parameters(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return list(contract.get("review_parameters") or [])


def all_supplier_inputs(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return list(contract.get("supplier_inputs") or [])


def required_review_parameters(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [param for param in all_review_parameters(contract) if param.get("required")]


def production_repeated_row_params(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Repeated-row review_parameters the calculator actually reads item-by-item in its
    production calc_method - not diagnostic-only breakdowns like trench_routes or
    communications_pipe_items, where the calculator reads a reviewed scalar instead and
    the row-by-row data is only a cross-check on sheet 03.

    See ADAPTER_BUILD_PLAN.md, "Критическое правило" section, for how the true/false
    split was verified (direct read of each calculator's source, 2026-07-12) - it is not
    inferrable from calculator_input_path alone, since diagnostic groups also declare one
    for their (currently inactive) alternate calc_method.
    """
    return [
        param
        for param in all_review_parameters(contract)
        if param.get("value_kind") == "repeated_rows" and param.get("production_input") is True
    ]


def diagnostic_repeated_row_params(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Repeated-row groups the calculator does NOT read item-by-item (production_input is not
    True) but that still render as a real per-item block on sheet 01 (2026-07-29 fix - they
    used to collapse to one permanently-blank scalar row). Mirrors
    build_review_workbook_from_contracts.diagnostic_repeated_row_params - kept in sync by hand
    since this package can't import across the sibling review_to_calculator boundary. Excludes
    review_behavior.show_to_user: false fields (foundation_wall_items, column_footing_items),
    which don't render on sheet 01 at all."""
    return [
        param
        for param in all_review_parameters(contract)
        if param.get("value_kind") == "repeated_rows"
        and param.get("production_input") is not True
        and (param.get("review_behavior") or {}).get("show_to_user") is not False
    ]


def price_keys(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return list(contract.get("price_keys") or [])


def defaults(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return list(contract.get("defaults") or [])


def default_by_key(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["key"]: item for item in defaults(contract)}


def price_key_by_key(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["key"]: item for item in price_keys(contract)}


def review_parameter_by_key(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["key"]: item
        for item in all_review_parameters(contract) + all_supplier_inputs(contract)
    }


def required_source_classes(contract: dict[str, Any]) -> list[str]:
    return list((contract.get("checks") or {}).get("required_source_classes") or [])


def calculator_input_mapping(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return list(contract.get("calculator_input_mapping") or [])
