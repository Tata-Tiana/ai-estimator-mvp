from __future__ import annotations

from typing import Any


def find_matching_value(
    candidate: dict[str, Any],
    hints: dict[str, Any],
) -> dict[str, Any] | None:
    """Find the best value_candidate matching unit/kind/range from hints.

    For elevation kind: value_decimal is stored negative (отм. -0.500);
    returns abs() so callers get a positive depth/height number.
    Returns the first match (extractor already orders by confidence).
    """
    expected_unit = hints.get('expected_unit')
    expected_kind = hints.get('expected_kind')
    value_range = hints.get('value_range')

    for vc in candidate.get('value_candidates', []):
        norm_unit = vc.get('normalized_unit', '')
        kind = vc.get('kind', '')
        val = vc.get('value_decimal')

        if val is None:
            continue

        if expected_unit and norm_unit != expected_unit:
            continue

        if expected_kind and kind != expected_kind:
            continue

        resolved_val = abs(val) if kind == 'elevation' else val

        if value_range:
            lo, hi = value_range
            if not (lo <= resolved_val <= hi):
                continue

        result = dict(vc)
        if kind == 'elevation':
            result['value_decimal'] = resolved_val
        return result

    return None


def extract_collect_field(
    candidate: dict[str, Any],
    field_hints: dict[str, Any],
) -> Any:
    """Extract one named field from a candidate for collect_all aggregation.

    source='subject_hint' → returns the candidate's subject_hint string directly.
    Otherwise, delegates to find_matching_value with the field's hints.
    """
    if field_hints.get('source') == 'subject_hint':
        return candidate.get('subject_hint', '')

    return find_matching_value(candidate, field_hints)
