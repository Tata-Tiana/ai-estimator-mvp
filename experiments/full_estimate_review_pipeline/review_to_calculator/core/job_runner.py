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


def _load_build_input_function(section_code: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    path = SECTIONS_DIR / section_code / "build_input.py"
    if not path.exists():
        raise JobRunnerError(
            f"{section_code}: sections/{section_code}/build_input.py does not exist yet "
            "(see ADAPTER_BUILD_PLAN.md, Этап 1/2 - it has not been written for this "
            "section)."
        )
    module = _load_module_from_path(f"build_input_{section_code}", path)
    build_fn = getattr(module, "build_calculator_input", None)
    if build_fn is None:
        raise JobRunnerError(f"{path}: no build_calculator_input() function.")
    return build_fn


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
