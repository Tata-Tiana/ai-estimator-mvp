"""Tests for evidence_layer.py.

All fixtures are synthetic – no real project files, filenames, page numbers
or values from any specific project are used."""
import pytest
from evidence_layer import _build_evidence_from_data


# ── Synthetic minimal fixtures ─────────────────────────────────────────────

def _make_page(
    pdf: str = 'test.pdf',
    page: int = 1,
    text: str = '',
    title: str = '',
    sheet_type: str = 'unknown',
    drawing_num: str = '',
) -> dict:
    return {
        'source_pdf': pdf,
        'physical_page_number': page,
        'raw_page_text': text,
        'logical_sheet_title': title,
        'logical_sheet_type': sheet_type,
        'drawing_sheet_number': drawing_num,
    }


def _make_table(
    pdf: str = 'test.pdf',
    page: int = 1,
    t_idx: int = 1,
    rows: list | None = None,
    table_title: str | None = None,
) -> dict:
    t: dict = {
        'source_pdf': pdf,
        'physical_page_number': page,
        'table_index': t_idx,
        'rows': rows or [],
    }
    if table_title is not None:
        t['table_title'] = table_title
    return t


# ── evidence_id uniqueness ─────────────────────────────────────────────────

def test_evidence_ids_are_unique() -> None:
    pages = [
        _make_page(page=1, text='Площадь котлована - 100 м2'),
        _make_page(page=2, text='Геотекстиль 300 м2'),
    ]
    tables = [
        _make_table(page=3, rows=[['Наименование', 'Кол-во'], ['Песок', '50 м3']]),
    ]
    evidence = _build_evidence_from_data(pages, tables)
    ids = [e['evidence_id'] for e in evidence]
    assert len(ids) == len(set(ids)), 'evidence_id values must be unique'


# ── raw_text is never modified ─────────────────────────────────────────────

def test_raw_text_preserved() -> None:
    raw = 'Площадькотлована-100,0м2'
    pages = [_make_page(page=1, text=raw)]
    evidence = _build_evidence_from_data(pages, [])
    page_ev = [e for e in evidence if e['source_kind'] == 'page_text']
    assert page_ev, 'Expected page_text evidence'
    assert page_ev[0]['raw_text'] == raw, 'raw_text must not be modified'


# ── normalized_text differs from raw when normalization applies ───────────

def test_normalized_text_differs_from_raw() -> None:
    raw = 'Площадькотлована-100,0м2'
    pages = [_make_page(page=1, text=raw)]
    evidence = _build_evidence_from_data(pages, [])
    page_ev = [e for e in evidence if e['source_kind'] == 'page_text']
    assert page_ev[0]['normalized_text'] != raw


# ── table evidence when page text is empty ─────────────────────────────────

def test_table_evidence_created_when_page_text_empty() -> None:
    pages = [_make_page(page=1, text='')]  # empty page text (like CAD PDFs)
    tables = [
        _make_table(page=1, rows=[
            ['Наименование', 'Кол-во', 'Ед.изм'],
            ['Геотекстиль', '300', 'м2'],
            ['Песок', '50', 'м3'],
        ]),
    ]
    evidence = _build_evidence_from_data(pages, tables)
    table_rows = [e for e in evidence if e['source_kind'] == 'table_row']
    assert len(table_rows) >= 2, (
        'Table row evidence must be created even when page text is empty'
    )


# ── evidence contains required fields ─────────────────────────────────────

def test_evidence_has_required_fields() -> None:
    pages = [_make_page(page=1, text='Глубина котлована - 0,8 м')]
    evidence = _build_evidence_from_data(pages, [])
    for ev in evidence:
        assert 'evidence_id' in ev
        assert 'source_pdf' in ev
        assert 'physical_page_number' in ev
        assert 'source_kind' in ev
        assert 'raw_text' in ev
        assert 'normalized_text' in ev


# ── table row evidence has meta with headers and neighbors ────────────────

def test_table_row_meta_contains_headers_and_neighbors() -> None:
    rows = [
        ['Наименование', 'Длина, м', 'Объем, м3'],
        ['К1', '45,0', '18,5'],
        ['К2', '30,0', '12,0'],
    ]
    tables = [_make_table(rows=rows)]
    evidence = _build_evidence_from_data([], tables)
    table_rows = [e for e in evidence if e['source_kind'] == 'table_row']
    assert table_rows, 'Expected table_row evidence'
    # First data row should have headers in meta
    first_row = table_rows[0]
    assert first_row['meta']['table_headers'], 'table_headers should not be empty'
    # Middle row should have previous and next
    if len(table_rows) >= 2:
        mid = table_rows[1]
        assert mid['meta']['previous_row_text'], 'previous_row_text should be set'


# ── empty rows are skipped ────────────────────────────────────────────────

def test_empty_table_rows_are_skipped() -> None:
    rows = [
        ['', '', ''],          # all empty
        ['Геотекстиль', '200', 'м2'],
        ['', None, ''],        # effectively empty
    ]
    tables = [_make_table(rows=rows)]
    evidence = _build_evidence_from_data([], tables)
    table_rows = [e for e in evidence if e['source_kind'] == 'table_row']
    assert len(table_rows) == 1, 'Empty rows must be skipped'


# ── source_pdf and physical_page_number are always set ────────────────────

def test_source_pdf_and_page_number_always_set() -> None:
    pages = [_make_page(pdf='project.pdf', page=5, text='Площадь - 100 м2')]
    evidence = _build_evidence_from_data(pages, [])
    for ev in evidence:
        if ev['source_kind'] == 'page_text':
            assert ev['source_pdf'] == 'project.pdf'
            assert ev['physical_page_number'] == 5


# ── drawing_index entries become evidence ────────────────────────────────

def test_drawing_index_creates_evidence() -> None:
    drawing_index = [
        {
            'source_pdf': 'project.pdf',
            'drawing_sheet_number': '3',
            'drawing_sheet_title': 'Схема расположения трасс',
            'physical_page_number': 4,
            'evidence_text': '3 Схема расположения трасс',
        }
    ]
    evidence = _build_evidence_from_data([], [], drawing_index)
    di_ev = [e for e in evidence if e['source_kind'] == 'drawing_index']
    assert di_ev, 'drawing_index entries should produce evidence'


# ── table row enriched with page metadata when available ─────────────────

def test_table_row_inherits_page_logical_type() -> None:
    pages = [_make_page(page=2, sheet_type='earthworks_pit_plan', title='План котлована')]
    tables = [_make_table(page=2, rows=[['Площадь котлована', '100', 'м2']])]
    evidence = _build_evidence_from_data(pages, tables)
    row_ev = [e for e in evidence if e['source_kind'] == 'table_row']
    assert row_ev
    assert row_ev[0]['logical_sheet_type'] == 'earthworks_pit_plan'
    assert row_ev[0]['logical_sheet_title'] == 'План котлована'


# ── A4.2.2: section_code propagation ──────────────────────────────────────

def _make_page_with_section(
    pdf: str = 'test.pdf',
    page: int = 1,
    text: str = 'Площадь 100 м2',
    title: str = 'Тест',
    sheet_type: str = 'earthworks_pit_plan',
    section: str = 'earthworks',
) -> dict:
    return {
        'source_pdf': pdf,
        'physical_page_number': page,
        'raw_page_text': text,
        'logical_sheet_title': title,
        'logical_sheet_type': sheet_type,
        'drawing_sheet_number': '',
        'section_code': section,
    }


def test_section_code_propagated_to_page_evidence() -> None:
    """page_text evidence must carry section_code from the logical_page."""
    pages = [_make_page_with_section(section='earthworks')]
    evidence = _build_evidence_from_data(pages, [])
    page_ev = [e for e in evidence if e['source_kind'] == 'page_text']
    assert page_ev
    assert page_ev[0]['section_code'] == 'earthworks'
    assert page_ev[0]['page_section_code'] == 'earthworks'
    assert page_ev[0]['section_source'] == 'page'
    assert page_ev[0]['section_confidence'] == 1.0


def test_section_code_propagated_to_table_evidence() -> None:
    """table_row evidence must carry section_code from the page it lives on."""
    pages = [_make_page_with_section(page=1, section='foundation_slab')]
    tables = [_make_table(page=1, rows=[['Бетон', '42', 'м3']])]
    evidence = _build_evidence_from_data(pages, tables)
    row_ev = [e for e in evidence if e['source_kind'] == 'table_row']
    assert row_ev
    assert row_ev[0]['section_code'] == 'foundation_slab'
    assert row_ev[0]['section_source'] == 'page'


def test_unknown_section_page_produces_unknown_in_evidence() -> None:
    """Page with empty section_code → evidence gets section_code='unknown'."""
    pages = [_make_page_with_section(section='')]
    evidence = _build_evidence_from_data(pages, [])
    page_ev = [e for e in evidence if e['source_kind'] == 'page_text']
    assert page_ev
    assert page_ev[0]['section_code'] == 'unknown'
    assert page_ev[0]['section_source'] == 'unknown'
    assert page_ev[0]['section_confidence'] == 0.0


def test_missing_section_code_field_produces_unknown() -> None:
    """Page dict without section_code key → evidence gets 'unknown' (backward compat)."""
    page = _make_page(page=1, text='Площадь 100 м2')  # no section_code key
    evidence = _build_evidence_from_data([page], [])
    page_ev = [e for e in evidence if e['source_kind'] == 'page_text']
    assert page_ev
    assert page_ev[0]['section_code'] == 'unknown'


def test_table_context_title_is_logical_sheet_title() -> None:
    """table_row evidence must have table_context_title = logical_sheet_title of the page."""
    pages = [_make_page_with_section(page=1, title='Спецификация к фундаментной плите')]
    tables = [_make_table(page=1, rows=[['Бетон', '42', 'м3']])]
    evidence = _build_evidence_from_data(pages, tables)
    row_ev = [e for e in evidence if e['source_kind'] == 'table_row']
    assert row_ev
    assert row_ev[0]['table_context_title'] == 'Спецификация к фундаментной плите'


def test_page_text_evidence_has_empty_table_context_title() -> None:
    """page_text evidence table_context_title must be empty string."""
    pages = [_make_page_with_section()]
    evidence = _build_evidence_from_data(pages, [])
    page_ev = [e for e in evidence if e['source_kind'] == 'page_text']
    assert page_ev
    assert page_ev[0]['table_context_title'] == ''


# ── A4.2.5: mixed-page table_override ─────────────────────────────────────────

def test_table_override_when_page_known_but_table_strongly_disagrees() -> None:
    """page=waterproofing, table_title='Спецификация к фундаментной плите'
    → section_code=foundation_slab, section_source=table_override.

    table_title must be set explicitly: infer_table_context_title() falls back
    to logical_sheet_title only when the table dict has no 'table_title' key."""
    pages = [_make_page_with_section(page=1, section='waterproofing',
                                      sheet_type='cutoff_waterproofing_scheme',
                                      title='Схема гидроизоляции')]
    tables = [_make_table(page=1,
                          table_title='Спецификация к фундаментной плите',
                          rows=[['Бетон B25', '42', 'м3']])]
    evidence = _build_evidence_from_data(pages, tables)
    row_ev = [e for e in evidence if e['source_kind'] == 'table_row']
    assert row_ev
    assert row_ev[0]['section_code'] == 'foundation_slab', (
        f'Table title override must win. Got: {row_ev[0]["section_code"]}'
    )
    assert row_ev[0]['section_source'] == 'table_override'


def test_no_override_when_table_only_has_generic_materials() -> None:
    """page=waterproofing, table rows have only generic terms (бетон, арматура)
    without a strong title/header signal → page section must be kept."""
    pages = [_make_page_with_section(page=1, section='waterproofing',
                                      title='Схема гидроизоляции')]
    tables = [_make_table(page=1, rows=[['Поз.', 'Наименование', 'Кол.'],
                                         ['Бетон B25', '42', 'м3'],
                                         ['Арматура А500С', '1850', 'кг']])]
    evidence = _build_evidence_from_data(pages, tables)
    row_ev = [e for e in evidence if e['source_kind'] == 'table_row']
    assert row_ev
    assert row_ev[0]['section_code'] == 'waterproofing', (
        f'Generic material rows must not override known page. Got: {row_ev[0]["section_code"]}'
    )
    assert row_ev[0]['section_source'] == 'page'


def test_table_override_source_page_unknown_stays_table_not_table_override() -> None:
    """page=unknown, table classifies → section_source must be 'table', not 'table_override'."""
    pages = [_make_page_with_section(page=1, section='',
                                      title='Спецификация к плану кровли')]
    tables = [_make_table(page=1, rows=[['Спецификаци�� кровли'],
                                         ['LOGICROOF', '250', 'м2']])]
    evidence = _build_evidence_from_data(pages, tables)
    row_ev = [e for e in evidence if e['source_kind'] == 'table_row']
    assert row_ev
    assert row_ev[0]['section_source'] == 'table', (
        f'Page=unknown should give section_source=table, not table_override. '
        f'Got: {row_ev[0]["section_source"]}'
    )


def test_no_override_when_page_and_table_agree() -> None:
    """page=flat_roof, table also classifies as flat_roof → ordinary 'page' source kept."""
    pages = [_make_page_with_section(page=1, section='flat_roof',
                                      title='Спецификация кровли')]
    tables = [_make_table(page=1, rows=[['Спецификация кровли'],
                                         ['LOGICROOF', '250', 'м2']])]
    evidence = _build_evidence_from_data(pages, tables)
    row_ev = [e for e in evidence if e['source_kind'] == 'table_row']
    assert row_ev
    # table confirms page — no override needed, page wins
    assert row_ev[0]['section_code'] == 'flat_roof'
    assert row_ev[0]['section_source'] in ('page', 'table')
