"""Tests for Stage 2 evidence enrichment helpers in review_workbook_builder.

All fixtures are synthetic — no real project values, filenames, or PDF content."""
from __future__ import annotations

import pytest

from google_sheets.review_workbook_builder import (
    _evidence_priority,
    evidence_block_rows,
    filter_relevant_evidence,
    generic_candidate_block_rows,
    sort_generic_candidates,
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _make_ev(
    ev_id: str = 'ev_001',
    raw_text: str = '',
    source_kind: str = 'page_text',
    source_pdf: str = 'test.pdf',
    page: int = 1,
    meta: dict | None = None,
) -> dict:
    return {
        'evidence_id': ev_id,
        'source_pdf': source_pdf,
        'physical_page_number': page,
        'source_kind': source_kind,
        'raw_text': raw_text,
        'normalized_text': raw_text,
        'logical_sheet_title': '',
        'logical_sheet_type': '',
        'drawing_sheet_number': '',
        'meta': meta or {},
    }


def _make_cand(
    cand_id: str = 'cand_000001',
    candidate_type: str = 'route_summary',
    ev_id: str = 'ev_001',
    subject_hint: str = 'К1',
) -> dict:
    return {
        'candidate_id': cand_id,
        'candidate_type': candidate_type,
        'subject_hint': subject_hint,
        'property_hint': 'length',
        'value_candidates': [],
        'unit_candidates': [],
        'evidence_id': ev_id,
        'extractor': 'generic_candidate_extractor',
        'confidence': 0.85,
        'reason': 'route label found',
        'raw_text': 'К1 длина 28,4 п.м',
        'normalized_text': 'К1 длина 28,4 п.м',
    }


# ── filter_relevant_evidence ───────────────────────────────────────────────

def test_relevant_evidence_passes_engineering_text() -> None:
    ev = _make_ev(raw_text='К1 труба длина 28,4 п.м')
    assert filter_relevant_evidence([ev]), 'Engineering text should pass relevance filter'


def test_irrelevant_evidence_is_excluded() -> None:
    ev = _make_ev(raw_text='Общая пояснительная записка')
    assert not filter_relevant_evidence([ev]), 'Non-engineering text must not pass relevance filter'


def test_relevant_kotlovan_passes() -> None:
    ev = _make_ev(raw_text='Площадь котлована 123,4 м2')
    assert filter_relevant_evidence([ev]), 'котлован text must pass'


def test_relevant_material_passes() -> None:
    ev = _make_ev(raw_text='Геотекстиль 300 м2')
    assert filter_relevant_evidence([ev]), 'Material evidence must pass relevance filter'


def test_relevant_pipe_passes() -> None:
    ev = _make_ev(raw_text='Труба ПНД Ø110 мм 45,0 п.м')
    assert filter_relevant_evidence([ev]), 'Pipe evidence must pass relevance filter'


# ── priority / sorting ─────────────────────────────────────────────────────

def test_table_row_has_higher_priority_than_page_text() -> None:
    ev_table = _make_ev(ev_id='t', raw_text='К1 длина 28 п.м', source_kind='table_row')
    ev_page = _make_ev(ev_id='p', raw_text='К1 длина 28 п.м', source_kind='page_text')
    assert _evidence_priority(ev_table) < _evidence_priority(ev_page), \
        'table_row must have lower (better) priority score than page_text'


def test_evidence_with_quantity_unit_ranked_higher_than_without() -> None:
    ev_with = _make_ev(ev_id='a', raw_text='котлован 1,2 м')
    ev_without = _make_ev(ev_id='b', raw_text='котлован текст')
    assert _evidence_priority(ev_with) <= _evidence_priority(ev_without)


def test_sorted_table_row_appears_first() -> None:
    ev_page = _make_ev(ev_id='p', raw_text='К1 длина 28 п.м', source_kind='page_text')
    ev_table = _make_ev(ev_id='t', raw_text='К1 длина 28 п.м', source_kind='table_row')
    result = filter_relevant_evidence([ev_page, ev_table])
    assert result[0]['source_kind'] == 'table_row', 'table_row must appear first after sort'


# ── limit ─────────────────────────────────────────────────────────────────

def test_filter_respects_limit() -> None:
    evidence = [_make_ev(ev_id=f'ev_{i}', raw_text='К1 длина 28 п.м') for i in range(200)]
    result = filter_relevant_evidence(evidence, limit=50)
    assert len(result) == 50, 'filter_relevant_evidence must respect the limit parameter'


def test_filter_returns_all_when_below_limit() -> None:
    evidence = [_make_ev(ev_id='ev_1', raw_text='труба ПНД 28 п.м')]
    result = filter_relevant_evidence(evidence, limit=500)
    assert len(result) == 1


# ── evidence_block_rows ───────────────────────────────────────────────────

def test_evidence_block_rows_structure() -> None:
    ev = _make_ev(
        ev_id='ev_001', raw_text='К1 длина 28 п.м', source_kind='table_row',
        meta={'table_index': 2, 'row_index': 3},
    )
    rows = evidence_block_rows([ev])
    assert len(rows) == 1
    row = rows[0]
    assert row[0] == 'ev_001'    # evidence_id
    assert row[6] == 'table_row' # source_kind
    assert row[7] == 2           # table_index from meta
    assert row[8] == 3           # row_index from meta


def test_evidence_block_rows_raw_text_truncated() -> None:
    long_text = 'К1 ' + 'x' * 1000
    ev = _make_ev(raw_text=long_text)
    rows = evidence_block_rows([ev])
    assert len(rows[0][9]) <= 800, 'raw_text must be truncated to 800 chars'


# ── sort_generic_candidates ───────────────────────────────────────────────

def test_sort_generic_candidates_order() -> None:
    cands = [
        _make_cand(cand_id='c3', candidate_type='unknown_relevant_quantity'),
        _make_cand(cand_id='c1', candidate_type='route_summary'),
        _make_cand(cand_id='c2', candidate_type='pipe_item'),
    ]
    result = sort_generic_candidates(cands)
    types = [c['candidate_type'] for c in result]
    assert types.index('route_summary') < types.index('pipe_item')
    assert types.index('pipe_item') < types.index('unknown_relevant_quantity')


def test_sort_generic_candidates_respects_limit() -> None:
    cands = [_make_cand(cand_id=f'c{i}') for i in range(300)]
    result = sort_generic_candidates(cands, limit=100)
    assert len(result) == 100


# ── generic_candidate_block_rows: enrichment from evidence ────────────────

def test_generic_candidate_enriched_from_evidence() -> None:
    cand = _make_cand(ev_id='ev_999')
    ev = _make_ev(ev_id='ev_999', source_pdf='project.pdf', page=5)
    rows = generic_candidate_block_rows([cand], {'ev_999': ev})
    assert rows[0][10] == 'project.pdf', 'source_pdf must be pulled from evidence index'
    assert rows[0][11] == '5', 'physical_page_number must be pulled from evidence index (as str)'


def test_generic_candidate_missing_evidence_does_not_crash() -> None:
    cand = _make_cand(ev_id='ev_missing')
    rows = generic_candidate_block_rows([cand], {})
    assert len(rows) == 1, 'Missing evidence must not raise an exception'
    assert 'evidence metadata not found' in str(rows[0][9]), \
        'reason must note missing evidence metadata'


def test_generic_candidate_uses_own_raw_text_if_available() -> None:
    cand = _make_cand(ev_id='ev_001')
    cand['raw_text'] = 'text from candidate itself'
    ev = _make_ev(ev_id='ev_001', raw_text='text from evidence')
    rows = generic_candidate_block_rows([cand], {'ev_001': ev})
    assert rows[0][12] == 'text from candidate itself', \
        'candidate raw_text takes precedence over evidence raw_text'


# ── graceful fallback for empty inputs ────────────────────────────────────

def test_filter_empty_evidence_returns_empty() -> None:
    assert filter_relevant_evidence([]) == []


def test_sort_empty_candidates_returns_empty() -> None:
    assert sort_generic_candidates([]) == []


def test_generic_candidate_rows_empty_returns_empty() -> None:
    assert generic_candidate_block_rows([], {}) == []
