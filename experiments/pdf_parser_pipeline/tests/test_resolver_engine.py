"""Tests for the A4 parameter resolver engine (parameter_resolver/).

All fixtures are synthetic — no real project PDFs, filenames, or page numbers.
Architecture contract enforced here:
  - resolver_engine reads resolver_hints only (NEVER regex_patterns)
  - positive_context: AND logic (all must match)
  - negative_context: OR reject logic (any match rejects)
  - prefer_context: soft bonus only, no rejection
  - elevation kind: abs() returned as positive depth
  - value_range: sanity filter, not disambiguation
  - collect_all: returns ordered list of items
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from experiments.pdf_parser_pipeline.parameter_resolver import resolve


# ── Fixture helpers ────────────────────────────────────────────────────────

def _param(
    code: str,
    hints: dict[str, Any] | None,
    regex_patterns: list[str] | None = None,
) -> dict[str, Any]:
    return {
        'parameter_code': code,
        'resolver_hints': hints,
        'regex_patterns': regex_patterns or [],
    }


def _cand(
    cand_id: str,
    ctype: str,
    norm_text: str,
    subject: str,
    values: list[dict[str, Any]],
    confidence: float = 0.75,
) -> dict[str, Any]:
    return {
        'candidate_id': cand_id,
        'candidate_type': ctype,
        'normalized_text': norm_text,
        'subject_hint': subject,
        'value_candidates': values,
        'confidence': confidence,
    }


def _val(
    raw: str,
    decimal: float,
    unit: str,
    kind: str = 'area',
) -> dict[str, Any]:
    return {
        'raw_value': raw,
        'value_decimal': decimal,
        'normalized_unit': unit,
        'kind': kind,
    }


# ── Basic: no hints / no candidates ───────────────────────────────────────

def test_no_hints_returns_missing() -> None:
    result = resolve(_param('test_param', hints=None), [])
    assert result['status'] == 'missing'
    assert result['parameter_code'] == 'test_param'


def test_no_candidates_returns_missing() -> None:
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'площадь'],
    }
    result = resolve(_param('pit_area', hints), candidates=[])
    assert result['status'] == 'missing'


def test_wrong_candidate_type_filtered() -> None:
    """Candidate with wrong type is ignored even if context + value match."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'площадь'],
    }
    cands = [
        _cand('c1', 'route_summary', 'площадь котлована 100 м2', 'площадь', [
            _val('100', 100.0, 'm2'),
        ]),
    ]
    result = resolve(_param('pit_area', hints), cands)
    assert result['status'] == 'missing'


# ── positive_context: AND logic ────────────────────────────────────────────

def test_positive_context_partial_match_rejected() -> None:
    """Only one of two required patterns matches → missing."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'площадь', r'котлован'],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'площадь фундамента 100 м2', 'площадь', [
            _val('100', 100.0, 'm2'),
        ]),
    ]
    result = resolve(_param('pit_area', hints), cands)
    assert result['status'] == 'missing'


def test_positive_context_all_match_found() -> None:
    """All positive_context patterns match → found."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'площадь', r'котлован'],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'площадь котлована 150 м2', 'площадь', [
            _val('150', 150.0, 'm2'),
        ]),
    ]
    result = resolve(_param('pit_area', hints), cands)
    assert result['status'] == 'found'
    assert result['value_decimal'] == 150.0
    assert result['normalized_unit'] == 'm2'
    assert result['source_candidate_id'] == 'c1'


# ── negative_context: OR logic ─────────────────────────────────────────────

def test_negative_context_any_match_rejects() -> None:
    """Any negative_context pattern match → candidate rejected."""
    hints = {
        'expected_unit': 'm3',
        'candidate_types': ['material_quantity'],
        'negative_context': [r'арматур', r'бетон'],
    }
    cands = [
        _cand('c1', 'material_quantity', 'бетон В22,5 42 м3', 'бетон', [
            _val('42', 42.0, 'm3', kind='volume'),
        ]),
    ]
    result = resolve(_param('sand_volume', hints), cands)
    assert result['status'] == 'missing'


def test_negative_context_no_match_passes() -> None:
    """No negative_context match → candidate proceeds."""
    hints = {
        'expected_unit': 'm3',
        'candidate_types': ['label_value_quantity'],
        'negative_context': [r'арматур', r'бетон'],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'Песок объём 30 м3', 'Песок', [
            _val('30', 30.0, 'm3', kind='volume'),
        ]),
    ]
    result = resolve(_param('sand_volume', hints), cands)
    assert result['status'] == 'found'
    assert result['value_decimal'] == 30.0


# ── prefer_context: soft bonus ─────────────────────────────────────────────

def test_prefer_context_no_match_still_resolves() -> None:
    """prefer_context: missing match is OK — candidate resolves anyway."""
    hints = {
        'expected_unit': 'linear_m',
        'candidate_types': ['route_summary'],
        'positive_context': [r'К[0-9]|В[0-9]'],
        'prefer_context': [r'ИТОГО'],
    }
    cands = [
        _cand('c1', 'route_summary', 'К1 длина 50,5 п.м', 'К1', [
            _val('50,5', 50.5, 'linear_m', kind='linear_length'),
        ]),
    ]
    result = resolve(_param('trench_length', hints), cands)
    assert result['status'] == 'found'
    assert result['value_decimal'] == 50.5


def test_prefer_context_raises_confidence() -> None:
    """prefer_context match raises confidence over identical candidate without it."""
    hints = {
        'expected_unit': 'linear_m',
        'candidate_types': ['route_summary'],
        'positive_context': [r'К[0-9]|В[0-9]'],
        'prefer_context': [r'ИТОГО'],
    }
    cand_with = _cand('with_itogo', 'route_summary', 'К1 ИТОГО длина 50 п.м', 'К1', [
        _val('50', 50.0, 'linear_m', kind='linear_length'),
    ], confidence=0.70)
    cand_without = _cand('no_itogo', 'route_summary', 'К1 длина 50 п.м', 'К1', [
        _val('50', 50.0, 'linear_m', kind='linear_length'),
    ], confidence=0.70)

    result_with = resolve(_param('trench_length', hints), [cand_with])
    result_without = resolve(_param('trench_length', hints), [cand_without])

    assert result_with['status'] == 'found'
    assert result_without['status'] == 'found'
    assert result_with['confidence'] > result_without['confidence']


# ── elevation: abs() depth ─────────────────────────────────────────────────

def test_elevation_returns_abs_value() -> None:
    """Elevation stored as negative (-1.5) → resolver returns abs (1.5)."""
    hints = {
        'expected_unit': 'm',
        'expected_kind': 'elevation',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'глубин|котлован'],
        'value_range': [0.1, 20.0],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'Глубина котлована отм. -1,500 м', 'Глубина', [
            _val('-1,500', -1.5, 'm', kind='elevation'),
        ]),
    ]
    result = resolve(_param('pit_depth', hints), cands)
    assert result['status'] == 'found'
    assert result['value_decimal'] == 1.5


# ── value_range: sanity check ──────────────────────────────────────────────

def test_value_range_rejects_below_minimum() -> None:
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'value_range': [10.0, 5000.0],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'площадь 3 м2', 'площадь', [
            _val('3', 3.0, 'm2'),
        ]),
    ]
    assert resolve(_param('some_area', hints), cands)['status'] == 'missing'


def test_value_range_accepts_in_range() -> None:
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'value_range': [10.0, 5000.0],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'площадь 500 м2', 'площадь', [
            _val('500', 500.0, 'm2'),
        ]),
    ]
    result = resolve(_param('some_area', hints), cands)
    assert result['status'] == 'found'
    assert result['value_decimal'] == 500.0


# ── collect_all aggregation ────────────────────────────────────────────────

def test_collect_all_returns_all_matching_candidates() -> None:
    hints = {
        'aggregation': 'collect_all',
        'candidate_types': ['route_summary'],
        'positive_context': [r'К[0-9]|В[0-9]'],
        'collect_fields': {
            'label':  {'source': 'subject_hint'},
            'length': {'expected_unit': 'linear_m'},
            'volume': {'expected_unit': 'm3'},
        },
    }
    cands = [
        _cand('c1', 'route_summary', 'К1 длина 50 п.м объём 25 м3', 'К1', [
            _val('50', 50.0, 'linear_m', kind='linear_length'),
            _val('25', 25.0, 'm3', kind='volume'),
        ]),
        _cand('c2', 'route_summary', 'В1 длина 30 п.м объём 15 м3', 'В1', [
            _val('30', 30.0, 'linear_m', kind='linear_length'),
            _val('15', 15.0, 'm3', kind='volume'),
        ]),
    ]
    result = resolve(_param('trench_routes', hints), cands)
    assert result['status'] == 'found'
    assert result['aggregation'] == 'collect_all'
    assert result['count'] == 2
    items = result['items']
    assert items[0]['label'] == 'К1'
    assert items[0]['length'] == 50.0
    assert items[0]['volume'] == 25.0
    assert items[1]['label'] == 'В1'
    assert items[1]['length'] == 30.0


def test_collect_all_no_matches_returns_missing() -> None:
    hints = {
        'aggregation': 'collect_all',
        'candidate_types': ['route_summary'],
        'positive_context': [r'К[0-9]'],
        'collect_fields': {'label': {'source': 'subject_hint'}},
    }
    cands = [
        _cand('c1', 'material_quantity', 'Бетон 42 м3', 'Бетон', [
            _val('42', 42.0, 'm3', kind='volume'),
        ]),
    ]
    assert resolve(_param('trench_routes', hints), cands)['status'] == 'missing'


# ── A4 architecture contract ───────────────────────────────────────────────

def test_resolver_engine_ignores_regex_patterns_at_runtime() -> None:
    """resolver_engine must NOT use regex_patterns (legacy field).

    Synthetic setup: regex_patterns would match the candidate text, but
    resolver_hints requires a different unit and context.
    Engine must return missing — not fall back to regex_patterns.
    """
    regex_patterns = [r'Площадь.*(\d+).*м2']  # would match candidate below

    hints = {
        'expected_unit': 'm3',                     # wants volume, not area
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'объём|котлован'],   # 'Площадь' doesn't match
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'Площадь 150 м2', 'Площадь', [
            _val('150', 150.0, 'm2'),  # area unit — doesn't match expected m3
        ]),
    ]
    result = resolve(_param('test_area', hints, regex_patterns), cands)
    assert result['status'] == 'missing', (
        f'resolver_engine read regex_patterns! '
        f'status={result["status"]}, value={result.get("value_decimal")}'
    )


# ── Best-candidate selection ───────────────────────────────────────────────

def test_picks_highest_confidence_candidate() -> None:
    """Among multiple passing candidates, highest confidence wins."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'площадь'],
    }
    cands = [
        _cand('low', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
            _val('100', 100.0, 'm2'),
        ], confidence=0.55),
        _cand('high', 'label_value_quantity', 'площадь 200 м2', 'площадь', [
            _val('200', 200.0, 'm2'),
        ], confidence=0.85),
    ]
    result = resolve(_param('some_area', hints), cands)
    assert result['status'] == 'found'
    assert result['source_candidate_id'] == 'high'
    assert result['value_decimal'] == 200.0


# ── A4.1: new behaviour ────────────────────────────────────────────────────

def test_min_confidence_rejects_low_score_candidate() -> None:
    """Candidate with score below min_confidence is rejected."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'min_confidence': 0.80,
    }
    cands = [
        _cand('low', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
            _val('100', 100.0, 'm2'),
        ], confidence=0.60),  # below 0.80 threshold
    ]
    result = resolve(_param('pit_area', hints), cands)
    assert result['status'] == 'missing'


def test_min_confidence_accepts_above_threshold() -> None:
    """Candidate with score at or above min_confidence passes."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'min_confidence': 0.70,
    }
    cands = [
        _cand('ok', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
            _val('100', 100.0, 'm2'),
        ], confidence=0.75),
    ]
    result = resolve(_param('pit_area', hints), cands)
    assert result['status'] == 'found'
    assert result['value_decimal'] == 100.0


def test_strict_expected_kind_rejects_no_kind() -> None:
    """expected_kind is strict: value_candidate with empty kind is rejected."""
    hints = {
        'expected_unit': 'm',
        'expected_kind': 'elevation',
        'candidate_types': ['label_value_quantity'],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'глубина 1,5 м', 'глубина', [
            {'raw_value': '1,5', 'value_decimal': 1.5, 'normalized_unit': 'm', 'kind': ''},
        ]),
    ]
    result = resolve(_param('pit_depth', hints), cands)
    assert result['status'] == 'missing'


def test_pick_best_conflict_detection() -> None:
    """When multiple candidates pass with values differing >10%, needs_review is set."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'площадь'],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
            _val('100', 100.0, 'm2'),
        ], confidence=0.90),
        _cand('c2', 'label_value_quantity', 'площадь 200 м2', 'площадь', [
            _val('200', 200.0, 'm2'),
        ], confidence=0.70),
    ]
    result = resolve(_param('pit_area', hints), cands)
    assert result['status'] == 'found'
    assert result['value_decimal'] == 100.0  # highest confidence wins
    assert result['needs_review'] is True
    assert len(result['alternatives']) == 1
    assert result['alternatives'][0]['value_decimal'] == 200.0


def test_pick_best_no_conflict_when_values_close() -> None:
    """Values within 10% of each other: no conflict, needs_review=False."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
        'positive_context': [r'площадь'],
    }
    cands = [
        _cand('c1', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
            _val('100', 100.0, 'm2'),
        ], confidence=0.90),
        _cand('c2', 'label_value_quantity', 'площадь 105 м2', 'площадь', [
            _val('105', 105.0, 'm2'),
        ], confidence=0.70),
    ]
    result = resolve(_param('pit_area', hints), cands)
    assert result['status'] == 'found'
    assert result['needs_review'] is False


def test_result_includes_source_fields() -> None:
    """Found result includes evidence_id, raw_text, normalized_text from candidate."""
    hints = {
        'expected_unit': 'm3',
        'candidate_types': ['label_value_quantity'],
    }
    cand = _cand('c1', 'label_value_quantity', 'Объём 50 м3', 'Объём', [
        _val('50', 50.0, 'm3', kind='volume'),
    ])
    cand['evidence_id'] = 'ev_000001'
    cand['raw_text'] = 'Объём 50 м3'
    cand['normalized_text'] = 'Объём 50 м3'

    result = resolve(_param('some_volume', hints), [cand])
    assert result['status'] == 'found'
    assert result['evidence_id'] == 'ev_000001'
    assert result['raw_text'] == 'Объём 50 м3'
    assert result['normalized_text'] == 'Объём 50 м3'


def test_collect_all_marks_partial_items_needs_review() -> None:
    """Items missing required_collect_fields are marked needs_review=True."""
    hints = {
        'aggregation': 'collect_all',
        'candidate_types': ['route_summary'],
        'positive_context': [r'К[0-9]|В[0-9]'],
        'required_collect_fields': ['label', 'volume'],
        'collect_fields': {
            'label':  {'source': 'subject_hint'},
            'length': {'expected_unit': 'linear_m'},
            'volume': {'expected_unit': 'm3'},
        },
    }
    cands = [
        # Complete item: has label + volume
        _cand('c1', 'route_summary', 'К1 длина 50 п.м объём 25 м3', 'К1', [
            _val('50', 50.0, 'linear_m', kind='linear_length'),
            _val('25', 25.0, 'm3', kind='volume'),
        ]),
        # Partial item: has label but NO volume
        _cand('c2', 'route_summary', 'В1 длина 30 п.м', 'В1', [
            _val('30', 30.0, 'linear_m', kind='linear_length'),
        ]),
    ]
    result = resolve(_param('trench_routes', hints), cands)
    assert result['status'] == 'found'
    assert result['needs_review'] is True  # at least one partial item
    items = result['items']
    assert items[0]['needs_review'] is False  # complete item
    assert items[1]['needs_review'] is True   # missing volume
    assert 'volume' in items[1]['missing_fields']


# ── A4.2.2: section-aware scoring ─────────────────────────────────────────

def test_same_section_candidate_gets_bonus() -> None:
    """Same-section candidate scores higher than identical cross-section one."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
    }
    same = _cand('same', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
        _val('100', 100.0, 'm2'),
    ], confidence=0.70)
    same['section_code'] = 'earthworks'

    cross = _cand('cross', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
        _val('100', 100.0, 'm2'),
    ], confidence=0.70)
    cross['section_code'] = 'foundation_slab'

    result_same = resolve(_param('pit_area', hints), [same],
                          param_section_code='earthworks', section_scope_mode='scored')
    result_cross = resolve(_param('pit_area', hints), [cross],
                           param_section_code='earthworks', section_scope_mode='scored')

    assert result_same['status'] == 'found'
    assert result_cross['status'] == 'found'
    assert result_same['confidence'] > result_cross['confidence']


def test_unknown_section_candidate_sets_needs_review() -> None:
    """Candidate with section_code='unknown' → needs_review=True on result."""
    hints = {
        'expected_unit': 'm2',
        'candidate_types': ['label_value_quantity'],
    }
    cand = _cand('c1', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
        _val('100', 100.0, 'm2'),
    ])
    cand['section_code'] = 'unknown'

    result = resolve(_param('pit_area', hints), [cand],
                     param_section_code='earthworks', section_scope_mode='scored')
    assert result['status'] == 'found'
    assert result['needs_review'] is True


def test_floor_slab_unknown_candidate_sets_needs_review() -> None:
    """Candidate with section_code='floor_slab_unknown' → needs_review=True."""
    hints = {'expected_unit': 'm2', 'candidate_types': ['label_value_quantity']}
    cand = _cand('c1', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
        _val('100', 100.0, 'm2'),
    ])
    cand['section_code'] = 'floor_slab_unknown'

    result = resolve(_param('slab_area', hints), [cand],
                     param_section_code='floor_slab_1', section_scope_mode='scored')
    assert result['status'] == 'found'
    assert result['needs_review'] is True


def test_section_scope_mode_off_ignores_section() -> None:
    """section_scope_mode='off' → section_code has no effect on score or needs_review."""
    hints = {'expected_unit': 'm2', 'candidate_types': ['label_value_quantity']}
    cand = _cand('c1', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
        _val('100', 100.0, 'm2'),
    ], confidence=0.70)
    cand['section_code'] = 'foundation_slab'  # cross-section from earthworks POV

    result = resolve(_param('pit_area', hints), [cand],
                     param_section_code='earthworks', section_scope_mode='off')
    assert result['status'] == 'found'
    assert result['needs_review'] is False
    assert result['confidence'] == pytest.approx(0.70, abs=0.01)


def test_cross_section_candidate_gets_penalty() -> None:
    """Cross-section candidate (different known section) gets score penalty."""
    hints = {'expected_unit': 'm2', 'candidate_types': ['label_value_quantity']}
    cand = _cand('c1', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
        _val('100', 100.0, 'm2'),
    ], confidence=0.70)
    cand['section_code'] = 'flat_roof'

    result_scored = resolve(_param('pit_area', hints), [cand],
                            param_section_code='earthworks', section_scope_mode='scored')
    result_off = resolve(_param('pit_area', hints), [cand],
                         param_section_code='earthworks', section_scope_mode='off')

    assert result_scored['status'] == 'found'
    assert result_scored['confidence'] < result_off['confidence']


def test_same_section_wins_over_cross_section() -> None:
    """When same-section and cross-section candidates both pass, same-section wins."""
    hints = {'expected_unit': 'm2', 'candidate_types': ['label_value_quantity']}

    same = _cand('same', 'label_value_quantity', 'площадь 100 м2', 'площадь', [
        _val('100', 100.0, 'm2'),
    ], confidence=0.70)
    same['section_code'] = 'earthworks'

    cross = _cand('cross', 'label_value_quantity', 'площадь 150 м2', 'площадь', [
        _val('150', 150.0, 'm2'),
    ], confidence=0.80)  # higher base confidence but wrong section
    cross['section_code'] = 'flat_roof'

    result = resolve(_param('pit_area', hints), [same, cross],
                     param_section_code='earthworks', section_scope_mode='scored')
    assert result['status'] == 'found'
    assert result['source_candidate_id'] == 'same'
