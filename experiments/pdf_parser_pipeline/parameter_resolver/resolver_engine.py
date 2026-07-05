from __future__ import annotations

from typing import Any

from .context_scorer import score_candidate
from .validation import find_matching_value, extract_collect_field

# Section codes treated as "ambiguous" — candidate is usable but needs review.
# floor_slab_unknown means we found a floor slab but couldn't determine which floor.
_AMBIGUOUS_SECTIONS: frozenset[str] = frozenset({'unknown', '', 'floor_slab_unknown'})


def resolve(
    param: dict[str, Any],
    candidates: list[dict[str, Any]],
    param_section_code: str = '',
    section_scope_mode: str = 'scored',
) -> dict[str, Any]:
    """Resolve one parameter against generic_candidates.

    Reads resolver_hints ONLY — never reads regex_patterns (legacy field).

    param_section_code: the section this parameter belongs to.
      Used for section-aware scoring in 'scored' mode.
    section_scope_mode: 'off' | 'scored'
      'off'    — no section scoring (original behaviour)
      'scored' — same section → +0.10 bonus; unknown → needs_review;
                 different section → −0.15 penalty (unless allow_cross_section)
    """
    code = param.get('parameter_code', '')
    hints = param.get('resolver_hints')

    if not hints:
        return _missing(code, 'no resolver_hints defined')

    if hints.get('aggregation') == 'collect_all':
        return _resolve_collect_all(code, hints, candidates, param_section_code, section_scope_mode)
    return _resolve_pick_best(code, hints, candidates, param_section_code, section_scope_mode)


# ── section scoring ────────────────────────────────────────────────────────

def _apply_section_scoring(
    score: float,
    cand_section: str,
    param_section: str,
    hints: dict[str, Any],
    section_scope_mode: str,
) -> tuple[float, bool]:
    """Return (adjusted_score, section_needs_review).

    section_needs_review=True means the selected candidate came from an
    ambiguous or cross-section source — Елена should verify the value.
    """
    if section_scope_mode == 'off' or not param_section:
        return score, False

    if cand_section == param_section:
        return min(1.0, score + 0.10), False

    if cand_section in _AMBIGUOUS_SECTIONS:
        return score, True  # usable but ambiguous

    # Different known section
    if hints.get('allow_cross_section', False):
        return score, True  # explicitly allowed, still flag
    return max(0.0, score - 0.15), False


# ── pick_best ──────────────────────────────────────────────────────────────

def _resolve_pick_best(
    code: str,
    hints: dict[str, Any],
    candidates: list[dict[str, Any]],
    param_section_code: str,
    section_scope_mode: str,
) -> dict[str, Any]:
    min_conf: float = hints.get('min_confidence', 0.0)
    allowed_types = set(hints.get('candidate_types', []))
    # (score, context_reason, matched_value, candidate, section_needs_review)
    passed: list[tuple[float, str, dict[str, Any], dict[str, Any], bool]] = []

    for cand in candidates:
        if allowed_types and cand.get('candidate_type') not in allowed_types:
            continue

        score, reason = score_candidate(cand, hints)
        if score == 0.0:
            continue

        score, sec_review = _apply_section_scoring(
            score, cand.get('section_code', 'unknown'),
            param_section_code, hints, section_scope_mode,
        )
        if score < min_conf:
            continue

        matched_value = find_matching_value(cand, hints)
        if matched_value is None:
            continue

        passed.append((score, reason, matched_value, cand, sec_review))

    if not passed:
        return _missing(code, 'no candidate passed context + value filters')

    passed.sort(key=lambda x: x[0], reverse=True)
    best_score, best_reason, best_value, best_cand, best_sec_review = passed[0]

    # Conflict: multiple candidates with meaningfully different values (>10%)
    conflict_review = False
    alternatives: list[dict[str, Any]] = []
    if len(passed) > 1:
        all_vals = [x[2]['value_decimal'] for x in passed if x[2].get('value_decimal') is not None]
        if all_vals:
            lo, hi = min(all_vals), max(all_vals)
            if lo > 0 and hi / lo > 1.1:
                conflict_review = True
                alternatives = [
                    {
                        'value_decimal': x[2]['value_decimal'],
                        'source_candidate_id': x[3].get('candidate_id', ''),
                        'confidence': round(x[0], 3),
                    }
                    for x in passed[1:]
                ]

    return {
        'status': 'found',
        'parameter_code': code,
        'value_decimal': best_value['value_decimal'],
        'raw_value': best_value.get('raw_value', ''),
        'normalized_unit': best_value.get('normalized_unit', ''),
        'source_candidate_id': best_cand.get('candidate_id', ''),
        'evidence_id': best_cand.get('evidence_id', ''),
        'raw_text': best_cand.get('raw_text', ''),
        'normalized_text': best_cand.get('normalized_text', ''),
        'candidate_section_code': best_cand.get('section_code', 'unknown'),
        'confidence': round(best_score, 3),
        'needs_review': conflict_review or best_sec_review,
        'alternatives': alternatives,
        'reason': best_reason,
    }


# ── collect_all ────────────────────────────────────────────────────────────

def _resolve_collect_all(
    code: str,
    hints: dict[str, Any],
    candidates: list[dict[str, Any]],
    param_section_code: str,
    section_scope_mode: str,
) -> dict[str, Any]:
    min_conf: float = hints.get('min_confidence', 0.0)
    allowed_types = set(hints.get('candidate_types', []))
    collect_fields: dict[str, Any] = hints.get('collect_fields', {})
    required_fields = set(hints.get('required_collect_fields', []))
    items: list[dict[str, Any]] = []
    source_ids: list[str] = []
    any_needs_review = False

    for cand in candidates:
        if allowed_types and cand.get('candidate_type') not in allowed_types:
            continue

        score, _ = score_candidate(cand, hints)
        if score == 0.0:
            continue

        score, sec_review = _apply_section_scoring(
            score, cand.get('section_code', 'unknown'),
            param_section_code, hints, section_scope_mode,
        )
        if score < min_conf:
            continue

        item: dict[str, Any] = {}
        for field_name, field_hints in collect_fields.items():
            extracted = extract_collect_field(cand, field_hints)
            if isinstance(extracted, dict):
                item[field_name] = extracted.get('value_decimal')
                item[f'{field_name}_unit'] = extracted.get('normalized_unit', '')
            else:
                item[field_name] = extracted

        missing_fields = [f for f in required_fields if item.get(f) is None]
        item_needs_review = bool(missing_fields) or sec_review
        item['needs_review'] = item_needs_review
        item['missing_fields'] = missing_fields
        if item_needs_review:
            any_needs_review = True

        item['source_candidate_id'] = cand.get('candidate_id', '')
        item['evidence_id'] = cand.get('evidence_id', '')
        item['raw_text'] = cand.get('raw_text', '')
        item['candidate_section_code'] = cand.get('section_code', 'unknown')
        item['confidence'] = round(score, 3)
        items.append(item)
        source_ids.append(cand.get('candidate_id', ''))

    if items:
        return {
            'status': 'found',
            'parameter_code': code,
            'aggregation': 'collect_all',
            'items': items,
            'source_candidate_ids': source_ids,
            'count': len(items),
            'needs_review': any_needs_review,
            'reason': f'collected {len(items)} candidates',
        }

    return _missing(code, 'no candidates passed filters for collect_all')


# ── helpers ────────────────────────────────────────────────────────────────

def _missing(code: str, reason: str) -> dict[str, Any]:
    return {
        'status': 'missing',
        'parameter_code': code,
        'value_decimal': None,
        'raw_value': None,
        'normalized_unit': None,
        'source_candidate_id': None,
        'evidence_id': None,
        'raw_text': None,
        'normalized_text': None,
        'candidate_section_code': None,
        'confidence': 0.0,
        'needs_review': False,
        'alternatives': [],
        'reason': reason,
    }
