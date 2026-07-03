"""Tests for generic_candidate_extractor.py.

All examples are synthetic – no project-specific values, filenames,
page numbers or real PDF data are used as fixtures."""
import pytest
from evidence_layer import _build_evidence_from_data
from generic_candidate_extractor import _extract_candidates_from_evidence


# ── Helpers ────────────────────────────────────────────────────────────────

def _evidence_from_text(text: str, source_kind: str = 'page_text') -> list[dict]:
    """Create minimal synthetic evidence from a single text string."""
    if source_kind == 'table_row':
        tables = [{'source_pdf': 'test.pdf', 'physical_page_number': 1,
                   'table_index': 1, 'rows': [[text]]}]
        return _build_evidence_from_data([], tables)
    pages = [{'source_pdf': 'test.pdf', 'physical_page_number': 1,
              'raw_page_text': text, 'logical_sheet_title': '',
              'logical_sheet_type': 'unknown', 'drawing_sheet_number': ''}]
    return _build_evidence_from_data(pages, [])


def _candidates_from_text(text: str, source_kind: str = 'page_text') -> list[dict]:
    evidence = _evidence_from_text(text, source_kind)
    return _extract_candidates_from_evidence(evidence)


# ── label_value_quantity ──────────────────────────────────────────────────

def test_label_value_area() -> None:
    cands = _candidates_from_text('Площадь котлована - 100 м2')
    matches = [c for c in cands if c['candidate_type'] == 'label_value_quantity']
    assert matches, f'Expected label_value_quantity, got types: {[c["candidate_type"] for c in cands]}'
    assert any('котлован' in c['subject_hint'].lower() for c in matches)


def test_label_value_depth() -> None:
    cands = _candidates_from_text('Глубина котлована - 0,8 м')
    matches = [c for c in cands if c['candidate_type'] == 'label_value_quantity']
    assert matches, f'Expected label_value_quantity, got types: {[c["candidate_type"] for c in cands]}'
    depth = [c for c in matches if c.get('property_hint') == 'depth']
    assert depth, f'Expected property_hint=depth, got: {[c.get("property_hint") for c in matches]}'


def test_label_value_with_colon_separator() -> None:
    cands = _candidates_from_text('Объём котлована: 250 м3')
    matches = [c for c in cands if c['candidate_type'] == 'label_value_quantity']
    assert matches, 'Expected label_value_quantity with colon separator'


# ── route_summary ─────────────────────────────────────────────────────────

def test_route_summary_with_itogo() -> None:
    # Synthetic route summary – values chosen to differ from any real project
    cands = _candidates_from_text('К1 ИТОГО длина 45,0 п.м объем 18,5 м3')
    matches = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert matches, f'Expected route_summary, got: {[c["candidate_type"] for c in cands]}'
    assert matches[0]['confidence'] >= 0.80


def test_route_summary_water_supply() -> None:
    cands = _candidates_from_text('В1 длина 22,0 п.м глубина 0,9 м')
    matches = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert matches, 'Expected route_summary for В1 (water supply label)'


def test_route_summary_drainage() -> None:
    cands = _candidates_from_text('Дренаж ИТОГО длина 60,0 п.м')
    matches = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert matches, 'Expected route_summary for Дренаж'


def test_route_summary_eo() -> None:
    cands = _candidates_from_text('ЭО объем 5,0 м3')
    matches = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert matches, 'Expected route_summary for ЭО (electrical route label)'


# ── pipe_item ─────────────────────────────────────────────────────────────

def test_pipe_item_pnd() -> None:
    cands = _candidates_from_text('ПНД труба Ø110 мм 45,0 п.м')
    matches = [c for c in cands if c['candidate_type'] == 'pipe_item']
    assert matches, f'Expected pipe_item, got: {[c["candidate_type"] for c in cands]}'


def test_pipe_item_corrugated() -> None:
    cands = _candidates_from_text('Гофро труба Ø200 мм 80,0 п.м')
    matches = [c for c in cands if c['candidate_type'] == 'pipe_item']
    assert matches, 'Expected pipe_item for corrugated pipe'


def test_pipe_item_confidence_higher_with_linear_unit() -> None:
    with_lin = _candidates_from_text('Труба ПНД Ø160 мм 30,0 п.м')
    without_lin = _candidates_from_text('Труба ПНД Ø160 мм')
    pipe_with = [c for c in with_lin if c['candidate_type'] == 'pipe_item']
    pipe_without = [c for c in without_lin if c['candidate_type'] == 'pipe_item']
    if pipe_with and pipe_without:
        assert pipe_with[0]['confidence'] >= pipe_without[0]['confidence']


# ── pipe_piece_qty ────────────────────────────────────────────────────────

def test_pipe_piece_qty_fitting() -> None:
    cands = _candidates_from_text('Колено 90° Ø110 - 4 шт')
    matches = [c for c in cands if c['candidate_type'] == 'pipe_piece_qty']
    assert matches, f'Expected pipe_piece_qty, got: {[c["candidate_type"] for c in cands]}'


# ── material_quantity ─────────────────────────────────────────────────────

def test_material_quantity_geotextile() -> None:
    cands = _candidates_from_text('Геотекстиль 300 м2')
    matches = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert matches, f'Expected material_quantity, got: {[c["candidate_type"] for c in cands]}'


def test_material_quantity_sand() -> None:
    cands = _candidates_from_text('Песок (300 мм) 75,0 м3')
    matches = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert matches, 'Expected material_quantity for sand'


def test_material_quantity_gravel() -> None:
    cands = _candidates_from_text('Щебень фр.20-40 мм - 30,0 м3')
    matches = [c for c in cands
               if c['candidate_type'] in ('material_quantity', 'label_value_quantity')]
    assert matches, 'Expected material or label_value candidate for gravel'


# ── table_quantity_row ────────────────────────────────────────────────────

def test_table_quantity_row_from_table_source() -> None:
    cands = _candidates_from_text('Котлован | 150 | м2', source_kind='table_row')
    assert cands, 'Expected at least one candidate from table row with engineering keyword'


# ── value_candidates populated ────────────────────────────────────────────

def test_value_candidates_populated() -> None:
    cands = _candidates_from_text('Площадь котлована - 100 м2')
    has_values = [c for c in cands if c.get('value_candidates')]
    assert has_values, 'At least one candidate should have value_candidates'
    for c in has_values:
        for vc in c['value_candidates']:
            assert 'raw_value' in vc
            assert 'normalized_unit' in vc


# ── evidence_id is propagated ─────────────────────────────────────────────

def test_candidate_has_evidence_id() -> None:
    cands = _candidates_from_text('Площадь котлована - 100 м2')
    for c in cands:
        assert c.get('evidence_id'), f'Candidate missing evidence_id: {c}'
        assert c['evidence_id'].startswith('ev_')


# ── extractor field ───────────────────────────────────────────────────────

def test_candidate_extractor_field() -> None:
    cands = _candidates_from_text('Площадь котлована - 100 м2')
    for c in cands:
        assert c.get('extractor') == 'generic_candidate_extractor'


# ── no candidates for irrelevant text ─────────────────────────────────────

def test_no_candidates_for_irrelevant_text() -> None:
    cands = _candidates_from_text('Проверка орфографии и пунктуации')
    assert not cands, f'Expected no candidates for irrelevant text, got: {cands}'


# ── no project-specific hardcoding (structural check) ────────────────────

def test_no_trc_specific_logic() -> None:
    """Verify extractor works for a synthetic project with different route names.
    If the extractor were project-specific, it would fail or return nothing here."""
    # Using a different network labelling scheme to ensure generality
    cands = _candidates_from_text('В2 ИТОГО длина 35,0 п.м объем 14,0 м3')
    route = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert route, 'Extractor must work for any route label, not just one specific project'
