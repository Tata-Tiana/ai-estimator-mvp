from __future__ import annotations

from typing import Any

from floor_slab_calculator import calculate_floor_slab_pour


def calculate_floor_slab_1(input_data: dict[str, Any]) -> dict[str, Any]:
    """Thin wrapper (FLOOR_SLAB_UNIFICATION_PLAN.md P1.2/P1.3) - zero overrides, so every new
    calc_method knob in calculate_floor_slab_pour() falls back to its floor_slab_1-compatible
    default and this stays byte-identical to the old inline function for all 19 regression cases.
    The shared engine moved to floor_slab_calculator.py (P1.3, 2026-08-09) so this file's own name
    no longer implies floor_slab_2 depends on floor_slab_1 - it's the other way around: this file
    is just one of the engine's callers."""
    return calculate_floor_slab_pour(input_data)
