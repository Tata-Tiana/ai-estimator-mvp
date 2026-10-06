"""Small shared catalog defaults for rebar repeated rows.

The PDF/chat extraction should bring the project quantity in running meters. Weight per
meter and rod length are catalog/supply facts, so adapters may fill them when the reviewed
row leaves those cells blank.
"""

from __future__ import annotations

from typing import Any

REBAR_KG_PER_M_BY_DIAMETER = {
    6: 0.222,
    8: 0.395,
    10: 0.617,
    12: 0.888,
    16: 1.58,
    20: 2.47,
    25: 3.85,
}

REBAR_ROD_LENGTH_BY_DIAMETER = {
    6: 6.0,
    8: 6.0,
    10: 11.7,
    12: 11.7,
    16: 11.7,
    20: 11.7,
    25: 11.7,
}


def diameter_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def fill_rebar_catalog_defaults(item: dict[str, Any], *, section: str) -> dict[str, Any]:
    """Return a copy with blank kg_per_meter/rod_length_m filled from the shared catalog."""
    diameter = diameter_int(item.get("diameter_mm"))
    if diameter is None:
        raise ValueError(f"{section}: rebar item has no valid diameter_mm: {item!r}")

    result = dict(item)
    if result.get("kg_per_meter") in (None, ""):
        kg_per_meter = REBAR_KG_PER_M_BY_DIAMETER.get(diameter)
        if kg_per_meter is None:
            raise ValueError(
                f"{section}: no catalog kg_per_meter for rebar diameter {diameter} mm"
            )
        result["kg_per_meter"] = kg_per_meter

    if result.get("rod_length_m") in (None, ""):
        rod_length_m = REBAR_ROD_LENGTH_BY_DIAMETER.get(diameter)
        if rod_length_m is None:
            raise ValueError(
                f"{section}: no catalog rod_length_m for rebar diameter {diameter} mm"
            )
        result["rod_length_m"] = rod_length_m

    return result
