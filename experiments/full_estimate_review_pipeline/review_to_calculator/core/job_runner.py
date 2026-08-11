"""Orchestrates one section end to end: load contract -> read filled review_workbook.xlsx
(sheets 01+02 only) -> resolve prices -> section-specific build_input.py -> calculator.

The only per-section code is `sections/<code>/build_input.py`
(`build_calculator_input(normalized_review) -> dict`, see ADAPTER_BUILD_PLAN.md,
Этап 1/2) - this module is the same for all 8 sections.

Calculators use two different entry-point conventions (found by reading all 8 sources,
2026-07-13):
- earthworks, foundation_slab, waterproofing, load_bearing_walls_lintels take a typed
  `<Section>Input` dataclass with a `from_dict()` classmethod.
- floor_slab_1, floor_slab_2, flat_roof, schiedel_vent_channels take a plain dict.
`_prepare_calculator_argument()` detects which one via the calculate function's own type
hint, so build_input.py only ever has to produce a plain dict either way.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Callable

from openpyxl import load_workbook

from core.contract_loader import calculator_module_path, load_contract
from core.price_resolver import resolve_prices
from core.workbook_reader import read_review_workbook

REPO_ROOT = Path(__file__).resolve().parents[4]
SECTIONS_DIR = Path(__file__).resolve().parents[1] / "sections"


class JobRunnerError(ValueError):
    pass


def _load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise JobRunnerError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    # Dataclasses defined in the loaded module resolve their own class's module via
    # sys.modules[cls.__module__] internally - without registering it first, that
    # lookup returns None and dataclass field-type resolution crashes.
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_build_input_module(section_code: str):
    path = SECTIONS_DIR / section_code / "build_input.py"
    if not path.exists():
        raise JobRunnerError(
            f"{section_code}: sections/{section_code}/build_input.py does not exist yet "
            "(see ADAPTER_BUILD_PLAN.md, Этап 1/2 - it has not been written for this "
            "section)."
        )
    return _load_module_from_path(f"build_input_{section_code}", path)


def _load_build_input_function(section_code: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    module = _load_build_input_module(section_code)
    build_fn = getattr(module, "build_calculator_input", None)
    if build_fn is None:
        raise JobRunnerError(
            f"sections/{section_code}/build_input.py: no build_calculator_input() function."
        )
    return build_fn


def _load_build_inputs_function(section_code: str) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    """P2 (FLOOR_SLAB_UNIFICATION_PLAN.md): the plural, N-pours-capable sibling of
    build_calculator_input() - only floor_slab_1/floor_slab_2 have one as of 2026-08-10.
    Falls back to wrapping the singular function's result in a 1-item list for every other
    section, so run_floor_slab_pours() below never needs a section-specific branch."""
    module = _load_build_input_module(section_code)
    build_fn = getattr(module, "build_calculator_inputs", None)
    if build_fn is not None:
        return build_fn
    single_build_fn = getattr(module, "build_calculator_input", None)
    if single_build_fn is None:
        raise JobRunnerError(
            f"sections/{section_code}/build_input.py: no build_calculator_input() function."
        )
    return lambda normalized_review: [single_build_fn(normalized_review)]


def _load_calculate_function(contract: dict[str, Any]) -> Callable[..., dict[str, Any]]:
    section_code = contract["section"]["code"]
    module_path = REPO_ROOT / calculator_module_path(contract)
    if not module_path.exists():
        raise JobRunnerError(f"{section_code}: calculator module not found at {module_path}")

    calc_dir = str(module_path.parent)
    if calc_dir not in sys.path:
        sys.path.insert(0, calc_dir)

    module = _load_module_from_path(module_path.stem, module_path)
    function_name = f"calculate_{section_code}"
    calculate_fn = getattr(module, function_name, None)
    if calculate_fn is None:
        raise JobRunnerError(f"{module_path}: no function named {function_name}()")
    return calculate_fn


def _prepare_calculator_argument(calculate_fn: Callable[..., Any], calculator_input: dict[str, Any]) -> Any:
    """Most calculators take a plain dict; four take a typed `<Section>Input` dataclass
    with a `from_dict()` classmethod instead - detected from the function's own first
    parameter type hint, not hardcoded per section. All 8 calculator modules use
    `from __future__ import annotations`, so annotations are strings at runtime -
    `eval_str=True` resolves them against the function's own module globals."""
    signature = inspect.signature(calculate_fn, eval_str=True)
    first_param = next(iter(signature.parameters.values()), None)
    annotation = None if first_param is None else first_param.annotation
    from_dict = getattr(annotation, "from_dict", None)
    if callable(from_dict):
        return from_dict(calculator_input)
    return calculator_input


def run_section(section_code: str, workbook_path: str | Path) -> dict[str, Any]:
    """Runs one section's full review-workbook-to-calculator-result flow. Raises
    JobRunnerError/PriceResolutionError with a specific reason before ever calling the
    calculator with incomplete data - never silently fills a gap."""
    contract = load_contract(section_code)
    wb = load_workbook(workbook_path)
    normalized_review = read_review_workbook(wb, contract)
    resolved_prices = resolve_prices(normalized_review["prices"], contract)
    normalized_review["resolved_prices"] = resolved_prices

    build_calculator_input = _load_build_input_function(section_code)
    calculator_input = build_calculator_input(normalized_review)

    calculate_fn = _load_calculate_function(contract)
    calculator_argument = _prepare_calculator_argument(calculate_fn, calculator_input)
    result = calculate_fn(calculator_argument)

    return {
        "section_code": section_code,
        "workbook_path": str(workbook_path),
        "normalized_review": normalized_review,
        "calculator_input": calculator_input,
        "result": result,
    }


FLOOR_SLABS_SECTION_CODE = "floor_slabs"


def run_floor_slab_pours(workbook_path: str | Path) -> list[dict[str, Any]]:
    """P5 (2026-08-11): the N-pours sibling of run_section() for the single floor_slabs section
    (SECTION_ORDER's other 6 sections stay on run_section() unchanged; floor_slabs is dynamic like
    P2-P3 always intended, just against ONE section with N floor_slab_zones[] rows now instead of
    two fixed floor_slab_1/floor_slab_2 sections each producing 1+ pours). Calls
    build_calculator_inputs() (plural) - review_to_calculator/sections/floor_slabs/build_input.py -
    which returns one calculator input per real physical slab, always (no [combined] fallback: an
    unattributable row is a readiness blocker raised directly by the adapter, per
    P5_SLAB_DATA_CONTRACT.md).

    Returns pours in floor_slab_zones[] order, each shaped like run_section()'s own return dict
    plus `pour_context` (that zone's display name, from calculator_input["case_meta"]
    ["pour_context"] - always set, never None, since every zone has a real display_name/zone_id)."""
    wb = load_workbook(workbook_path)
    contract = load_contract(FLOOR_SLABS_SECTION_CODE)
    normalized_review = read_review_workbook(wb, contract)
    normalized_review["resolved_prices"] = resolve_prices(normalized_review["prices"], contract)

    build_calculator_inputs = _load_build_inputs_function(FLOOR_SLABS_SECTION_CODE)
    calculator_inputs = build_calculator_inputs(normalized_review)

    calculate_fn = _load_calculate_function(contract)
    pours: list[dict[str, Any]] = []
    for calculator_input in calculator_inputs:
        pour_context = calculator_input.get("case_meta", {}).get("pour_context")
        calculator_argument = _prepare_calculator_argument(calculate_fn, calculator_input)
        result = calculate_fn(calculator_argument)
        pours.append(
            {
                "section_code": FLOOR_SLABS_SECTION_CODE,
                "pour_context": pour_context,
                "workbook_path": str(workbook_path),
                "calculator_input": calculator_input,
                "result": result,
            }
        )
    return pours


def build_floor_slabs_result(workbook_path: str | Path) -> dict[str, Any]:
    """P3 entry point (unchanged signature/return shape since P5 - export_calculator_results_to_
    estimate_workbook.py/build_all_section_results.py/build_floor_slabs_result_json.py all keep
    working with zero changes) - consolidates run_floor_slab_pours()'s per-pour results into
    {"section": "floor_slabs", "pours": [{"title", "estimate_lines"}, ...]}. However many real
    physical slabs a project has is exactly how many blocks land in the final smeta."""
    pours = run_floor_slab_pours(workbook_path)
    return {
        "section": "floor_slabs",
        "pours": [
            {
                "title": pour["pour_context"] or "Плита перекрытия/покрытия",
                "estimate_lines": pour["result"].get("estimate_lines") or [],
            }
            for pour in pours
        ],
    }
