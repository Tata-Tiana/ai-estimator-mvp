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


# floor_slab_1 today emits its own zone as pour_input["slab_zones"][0] (a full slab_zones[] row -
# thickness_m/concrete_grade/level included); floor_slab_2's pours don't carry that dict at all
# (its own slab_zones[] group is diagnostic-only, never fed into calculate_floor_slab_2()) - only
# pour_context (the zone's context string) is common to both. zone_meta is None for a fallback
# (unsplit) pour in either section.
FLOOR_SLAB_SECTION_CODES = ("floor_slab_1", "floor_slab_2")


def run_floor_slab_pours(workbook_path: str | Path) -> list[dict[str, Any]]:
    """P2 (FLOOR_SLAB_UNIFICATION_PLAN.md) entry point - the N-pours sibling of run_section() for
    floor_slab_1+floor_slab_2 specifically (SECTION_ORDER's other 6 sections stay on run_section()
    unchanged). Runs both sections' full review-workbook-to-calculator-result flow, but calls
    build_calculator_inputs() (plural) instead of build_calculator_input() (singular) so each
    section can return multiple pour results instead of always exactly one.

    Returns pours in floor_slab_1-then-floor_slab_2 order, each shaped like run_section()'s own
    return dict plus `pour_context` (the zone's slab_zones[].context, or None for a fallback/
    unsplit pour) and `zone_meta` (the full slab_zones[] row when available, for P3's eventual
    section-title building - see this module's own comment above). Zero zones anywhere still
    means at least one pour per section today (both build_calculator_inputs() implementations
    fall back to [combined] rather than [], matching run_section()'s existing required-field
    validation - a section with missing required data still raises, same as before P2)."""
    wb = load_workbook(workbook_path)
    pours: list[dict[str, Any]] = []
    for section_code in FLOOR_SLAB_SECTION_CODES:
        contract = load_contract(section_code)
        normalized_review = read_review_workbook(wb, contract)
        normalized_review["resolved_prices"] = resolve_prices(normalized_review["prices"], contract)

        build_calculator_inputs = _load_build_inputs_function(section_code)
        calculator_inputs = build_calculator_inputs(normalized_review)

        calculate_fn = _load_calculate_function(contract)
        for calculator_input in calculator_inputs:
            pour_context = calculator_input.get("pour_context")
            zone_meta = None
            if pour_context is not None:
                zones = calculator_input.get("slab_zones")
                if zones and zones[0].get("context") == pour_context:
                    zone_meta = zones[0]
            calculator_argument = _prepare_calculator_argument(calculate_fn, calculator_input)
            result = calculate_fn(calculator_argument)
            pours.append(
                {
                    "section_code": section_code,
                    "pour_context": pour_context,
                    "zone_meta": zone_meta,
                    "workbook_path": str(workbook_path),
                    "calculator_input": calculator_input,
                    "result": result,
                }
            )
    return pours


# P3 (FLOOR_SLAB_UNIFICATION_PLAN.md): fallback title for a pour that's still the section's own
# single unsplit result (pour_context is None) - today's real behavior for every project, since
# no real extraction has zone_context yet (P4). Once a section genuinely splits, each pour uses
# its own zone_context text as the title instead (real per-project data, not a fixed string).
FLOOR_SLAB_SECTION_TITLES = {
    "floor_slab_1": "Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 1-ГО ЭТАЖА",
    "floor_slab_2": "Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-ГО ЭТАЖА",
}


def build_floor_slabs_result(workbook_path: str | Path) -> dict[str, Any]:
    """P3 entry point - consolidates run_floor_slab_pours()'s per-pour results into the single
    consolidated shape export_calculator_results_to_estimate_workbook.py's dynamic floor-slabs
    block reads: {"section": "floor_slabs", "pours": [{"title", "estimate_lines"}, ...]}. Honestly
    reflects reality (per the user's own framing when choosing this design 2026-08-10): however
    many real pours exist is exactly how many blocks land in the final smeta - 2 today for every
    real project (no zone_context yet), more once P4 ships and a project's PDF actually splits."""
    pours = run_floor_slab_pours(workbook_path)
    return {
        "section": "floor_slabs",
        "pours": [
            {
                "title": pour["pour_context"] or FLOOR_SLAB_SECTION_TITLES[pour["section_code"]],
                "estimate_lines": pour["result"].get("estimate_lines") or [],
            }
            for pour in pours
        ],
    }
