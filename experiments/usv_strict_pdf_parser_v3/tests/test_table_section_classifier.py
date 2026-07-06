"""Tests for table_section_classifier.py.

All fixtures are synthetic — no real project PDFs, filenames, page numbers,
or project-specific values. Tests verify generic keyword rules only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from table_section_classifier import classify_table_section, infer_table_context_title


# ── Helpers ────────────────────────────────────────────────────────────────────

def _cls(title: str = '', headers: list[str] | None = None, rows: list[list[str]] | None = None) -> dict:
    return classify_table_section(title, headers or [], rows or [])


# ── Title-level (confidence 0.90) ─────────────────────────────────────────────

class TestTitleLevel:

    def test_foundation_slab_by_title(self) -> None:
        r = _cls(title='Спецификация к фундаментной плите')
        assert r['section_code'] == 'foundation_slab'
        assert r['confidence'] == pytest.approx(0.90)
        assert r['source'] == 'table_title'

    def test_termovstavki_title(self) -> None:
        r = _cls(title='Спецификация термовставок')
        assert r['section_code'] == 'foundation_slab'

    def test_plan_fundamentnoj_plity(self) -> None:
        r = _cls(title='План фундаментной плиты')
        assert r['section_code'] == 'foundation_slab'

    def test_flat_roof_title(self) -> None:
        r = _cls(title='Спецификация кровли')
        assert r['section_code'] == 'flat_roof'

    def test_plan_krovli_title(self) -> None:
        r = _cls(title='План кровли')
        assert r['section_code'] == 'flat_roof'

    def test_earthworks_title(self) -> None:
        r = _cls(title='План котлована')
        assert r['section_code'] == 'earthworks'

    def test_waterproofing_title(self) -> None:
        r = _cls(title='Вертикальная гидроизоляция')
        assert r['section_code'] == 'waterproofing'

    def test_walls_kladochny_plan(self) -> None:
        r = _cls(title='Кладочный план')
        assert r['section_code'] == 'load_bearing_walls_lintels'

    def test_walls_peremychki(self) -> None:
        r = _cls(title='Спецификация перемычек')
        assert r['section_code'] == 'load_bearing_walls_lintels'

    def test_schiedel_title(self) -> None:
        r = _cls(title='Schiedel вентиляционные каналы')
        assert r['section_code'] == 'schiedel_vent_channels'

    def test_ventilyacionnyj_kanal_title(self) -> None:
        r = _cls(title='Вентиляционный канал')
        assert r['section_code'] == 'schiedel_vent_channels'

    def test_floor_slab_1_explicit(self) -> None:
        r = _cls(title='Спецификация к плите перекрытия 1 этажа')
        assert r['section_code'] == 'floor_slab_1'

    def test_floor_slab_2_explicit(self) -> None:
        r = _cls(title='Спецификация к плите перекрытия 2 этажа')
        assert r['section_code'] == 'floor_slab_2'

    def test_floor_slab_nad_1_etazhem(self) -> None:
        r = _cls(title='Перекрытие над 1 этажом')
        assert r['section_code'] == 'floor_slab_1'

    def test_floor_slab_nad_2_etazhem(self) -> None:
        r = _cls(title='Перекрытие над 2 этажом')
        assert r['section_code'] == 'floor_slab_2'

    def test_floor_slab_unknown_armirovaniye_plity(self) -> None:
        """'армирование плиты' without floor number → floor_slab_unknown."""
        r = _cls(title='Верхнее дополнительное армирование плиты')
        assert r['section_code'] == 'floor_slab_unknown'

    def test_floor_slab_unknown_plita_perekrytiya(self) -> None:
        r = _cls(title='Спецификация к плите перекрытия')
        assert r['section_code'] == 'floor_slab_unknown'


# ── Disambiguation: foundation_slab beats floor_slab_unknown ──────────────────

class TestDisambiguation:

    def test_armirovaniye_fundamentnoj_plity_is_foundation_not_floor(self) -> None:
        """'армирование фундаментной плиты' must be foundation_slab, not floor_slab_unknown."""
        r = _cls(title='Армирование фундаментной плиты')
        assert r['section_code'] == 'foundation_slab', (
            f'Expected foundation_slab, got {r["section_code"]}'
        )

    def test_specifkaciya_fundamentnoj_is_foundation(self) -> None:
        r = _cls(title='Спецификация к фундаментной плите')
        assert r['section_code'] == 'foundation_slab'

    def test_floor_slab_1_beats_floor_slab_unknown(self) -> None:
        """Explicit floor number must win over generic slab rules."""
        r = _cls(title='Плита перекрытия 1 этажа')
        assert r['section_code'] == 'floor_slab_1'


# ── Header-level (confidence 0.75) ────────────────────────────────────────────

class TestHeaderLevel:

    def test_logicroof_in_headers(self) -> None:
        r = _cls(headers=['Наименование', 'LOGICROOF', 'Кол.'])
        assert r['section_code'] == 'flat_roof'
        assert r['confidence'] == pytest.approx(0.75)
        assert r['source'] == 'table_headers'

    def test_schiedel_in_headers(self) -> None:
        r = _cls(headers=['Поз.', 'Schiedel', 'Кол.'])
        assert r['section_code'] == 'schiedel_vent_channels'
        assert r['confidence'] == pytest.approx(0.75)

    def test_termovstavki_in_headers(self) -> None:
        r = _cls(headers=['Наименование', 'термовставки', 'Ед.'])
        assert r['section_code'] == 'foundation_slab'

    def test_aerator_in_headers(self) -> None:
        r = _cls(headers=['аэратор кровельный', 'шт.'])
        assert r['section_code'] == 'flat_roof'

    def test_xps_slope_in_headers(self) -> None:
        r = _cls(headers=['XPS slope', 'м2'])
        assert r['section_code'] == 'flat_roof'


# ── Row-level (confidence 0.55) ───────────────────────────────────────────────

class TestRowLevel:

    def test_logicroof_in_rows(self) -> None:
        r = _cls(rows=[['Наименование', 'Кол.', 'Ед.'], ['LOGICROOF 120', '250', 'м2']])
        assert r['section_code'] == 'flat_roof'
        assert r['confidence'] == pytest.approx(0.55)
        assert r['source'] == 'table_rows'

    def test_schiedel_in_rows(self) -> None:
        r = _cls(rows=[['Schiedel UNO Plus', '2', 'шт.']])
        assert r['section_code'] == 'schiedel_vent_channels'

    def test_planter_in_rows(self) -> None:
        r = _cls(rows=[['PLANTER geo', '30', 'м2']])
        assert r['section_code'] == 'earthworks'

    def test_termovstavki_in_rows(self) -> None:
        r = _cls(rows=[['Поз.', 'Наименование'], ['1', 'Термовставка угловая']])
        assert r['section_code'] == 'foundation_slab'


# ── Generic terms must NOT classify at row level ──────────────────────────────

class TestNoFalsePositives:

    def test_gazoboton_in_rows_does_not_classify(self) -> None:
        """'газобетон' is too generic — must not trigger walls_lintels from rows."""
        r = _cls(rows=[['Газобетон D400', '10', 'м3']])
        assert r['section_code'] == '', (
            f'газобетон alone must not classify. Got {r["section_code"]}'
        )

    def test_beton_in_rows_does_not_classify(self) -> None:
        r = _cls(rows=[['Бетон B25', '42', 'м3']])
        assert r['section_code'] == ''

    def test_armatura_in_rows_does_not_classify(self) -> None:
        r = _cls(rows=[['Арматура А500С', '1850', 'кг']])
        assert r['section_code'] == ''

    def test_no_signals_returns_empty(self) -> None:
        r = _cls(title='', headers=['Поз.', 'Наименование', 'Кол.'],
                 rows=[['1', 'Неизвестный материал', '10']])
        assert r['section_code'] == ''
        assert r['confidence'] == pytest.approx(0.0)
        assert r['source'] == 'none'


# ── infer_table_context_title ─────────────────────────────────────────────────

class TestInferTitle:

    def test_uses_table_title_if_present(self) -> None:
        table = {'table_title': 'Спецификация'}
        page = {'logical_sheet_title': 'Другой заголовок'}
        assert infer_table_context_title(table, page) == 'Спецификация'

    def test_falls_back_to_logical_sheet_title(self) -> None:
        table = {}
        page = {'logical_sheet_title': 'План котлована'}
        assert infer_table_context_title(table, page) == 'План котлована'

    def test_returns_empty_string_when_no_title(self) -> None:
        assert infer_table_context_title({}, {}) == ''
