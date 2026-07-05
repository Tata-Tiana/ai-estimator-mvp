"""Tests for logical_sheet_classifier.py.

Architecture rules enforced here:
  - No hardcoded elevation values (+3.480, +4.680, etc.) for floor slab detection.
  - No page numbers as logic.
  - No project-specific names (USV, TRC, etc.) as logic.
  - floor_slab_1 / floor_slab_2 only from explicit "1 этаж" / "2 этаж" text.
  - Ambiguous slab pages get floor_slab_unknown, not a guess.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logical_sheet_classifier import classify, section_code


# ── Helpers ────────────────────────────────────────────────────────────────

def sc(title: str = '', text: str = '') -> str:
    """Shortcut: classify then map to section_code."""
    return section_code(classify(text, title, 'test.pdf'))


# ── Hardcoded elevations must NOT trigger floor_slab classification ────────

def test_elevation_value_alone_does_not_classify_floor_slab() -> None:
    """'+3.480' alone must not trigger floor_slab_1 — it is a project elevation."""
    sheet_type = classify('', '+3.480', 'test.pdf')
    assert sheet_type != 'floor_slab_1_spec', (
        f'Hardcoded elevation +3.480 must not determine floor slab. Got: {sheet_type}'
    )


def test_elevation_in_title_does_not_classify_floor_slab_1() -> None:
    """'Плита перекрытия на отм. +3.480' — elevation in title → floor_slab_unknown."""
    result = sc(title='Плита перекрытия на отм. +3.480')
    assert result == 'floor_slab_unknown', (
        f'Elevation-only slab title must be floor_slab_unknown, got: {result}'
    )


def test_elevation_in_title_does_not_classify_floor_slab_2() -> None:
    """'Плита перекрытия на отм. +4.680' — elevation in title → floor_slab_unknown."""
    result = sc(title='Плита перекрытия на отм. +4.680')
    assert result == 'floor_slab_unknown', (
        f'Elevation-only slab title must be floor_slab_unknown, got: {result}'
    )


# ── Floor slab: explicit floor number → correct section ───────────────────

def test_floor_slab_1_by_explicit_floor_number() -> None:
    assert sc(title='Спецификация к плите перекрытия 1 этажа') == 'floor_slab_1'


def test_floor_slab_1_by_nad_etazhem() -> None:
    assert sc(title='Перекрытие над 1 этажом') == 'floor_slab_1'


def test_floor_slab_2_by_explicit_floor_number() -> None:
    assert sc(title='Спецификация к плите перекрытия 2 этажа') == 'floor_slab_2'


def test_floor_slab_2_by_nad_etazhem() -> None:
    assert sc(title='Перекрытие над 2 этажом') == 'floor_slab_2'


def test_floor_slab_no_number_is_unknown() -> None:
    """'Плита перекрытия' without floor number → floor_slab_unknown."""
    result = sc(title='Спецификация к плите перекрытия')
    assert result == 'floor_slab_unknown', f'Expected floor_slab_unknown, got: {result}'


# ── Previously missed pages — new generic rules ────────────────────────────

def test_plan_fundamentnoj_plity_is_foundation_slab() -> None:
    assert sc(title='План фундаментной плиты') == 'foundation_slab'


def test_obshchy_vid_fundamenta_is_foundation_slab() -> None:
    assert sc(title='Общий вид фундамента') == 'foundation_slab'


def test_plan_krovli_is_flat_roof() -> None:
    assert sc(title='План кровли') == 'flat_roof'


def test_specificatsiya_krovli_is_flat_roof() -> None:
    assert sc(title='Спецификация кровли') == 'flat_roof'


def test_kladochny_plan_is_walls() -> None:
    assert sc(title='Кладочный план') == 'load_bearing_walls_lintels'


def test_plan_etazha_is_walls() -> None:
    assert sc(title='Кладочный план на отм. + 0. 000') == 'load_bearing_walls_lintels'


# ── Existing rules still work ──────────────────────────────────────────────

def test_plan_kotlovan_is_earthworks() -> None:
    assert sc(title='План котлована') == 'earthworks'


def test_kotlovan_and_pesok_is_earthworks() -> None:
    assert sc(text='котлован 100 м2 песок 50 м3') == 'earthworks'


def test_termovstavki_is_foundation_slab() -> None:
    assert sc(title='План термовставок') == 'foundation_slab'


def test_peremychki_is_walls() -> None:
    assert sc(title='Спецификация перемычек') == 'load_bearing_walls_lintels'


def test_schiedel_is_schiedel() -> None:
    assert sc(title='Schiedel вентиляционный канал') == 'schiedel_vent_channels'


def test_waterproofing_otcechnaya() -> None:
    assert sc(title='Отсечная гидроизоляция') == 'waterproofing'


def test_waterproofing_vertikalnaya() -> None:
    assert sc(title='Вертикальная гидроизоляция') == 'waterproofing'


def test_unknown_page_returns_empty_section() -> None:
    """Unrecognised page → section_code returns empty string (→ 'unknown' in evidence)."""
    result = section_code(classify('Произвольный текст без строительных признаков', '', 'test.pdf'))
    assert result == '', f'Unknown page must produce empty section_code, got: {result!r}'


# ── section_code mapping completeness ─────────────────────────────────────

def test_section_code_mapping_covers_all_known_types() -> None:
    """All sheet_types the classifier can return must be in the mapping."""
    known_types = [
        'earthworks_pit_plan', 'communications_scheme',
        'foundation_slab_spec', 'thermal_inserts_plan',
        'cutoff_waterproofing_scheme',
        'walls_blocks_spec', 'lintels_plan', 'walls_layout_plan',
        'floor_slab_1_spec', 'floor_slab_2_spec', 'floor_slab_unknown_spec',
        'flat_roof_spec', 'schiedel_vent_spec',
    ]
    for st in known_types:
        result = section_code(st)
        assert result, f'section_code("{st}") returned empty — add it to the mapping'
