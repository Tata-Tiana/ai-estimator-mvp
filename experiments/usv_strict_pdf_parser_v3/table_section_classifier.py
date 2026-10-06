"""Table-level section attribution.

classify_table_section() determines the construction section of a table from
its title, headers, and first data rows — without LLM, page numbers, project-
specific filenames, or hardcoded elevation values.

Confidence levels:
  0.90  title match (same weight as page classifier)
  0.75  strong unique signal in table headers
  0.55  strong unique signal in first 3 data rows
  0.0   no signal found

Only truly unique terms are used for header/row classification to avoid false
positives (e.g. 'газобетон' in a roof parapet row must not flip to walls).
"""
from __future__ import annotations

import re
from typing import Any


# ── Helpers ────────────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    return ' '.join(str(text).lower().split())


def _join(items: list) -> str:
    return ' '.join(str(x) for x in items if x)


# ── Title-level rules (confidence 0.90) ───────────────────────────────────────
# Order matters: more specific rules must come before broader ones.

_TITLE_RULES: list[tuple[re.Pattern[str], str]] = [
    # foundation_slab — check BEFORE generic "плит" to avoid misclassifying
    # "армирование фундаментной плиты" as floor_slab_unknown
    (re.compile(
        r'фундаментн\w*\s+плит|термовставк\w*|термовставок|план\s+фундаментн'
        r'|общий\s+вид\s+фундамент|армирование\s+фундаментн'
        r'|спецификаци\w+\s+(?:к\s+)?фундаментн',
        re.I | re.U,
    ), 'foundation_slab'),

    # schiedel / vent channels
    (re.compile(r'schiedel|вентканал|вентиляционный\s+канал', re.I | re.U),
     'schiedel_vent_channels'),

    # flat_roof
    (re.compile(
        r'план\s+кровл|спецификаци\w+\s+кровл|кровл\w+\s+узел|узел\s+кровл',
        re.I | re.U,
    ), 'flat_roof'),

    # earthworks
    (re.compile(
        r'план\s+котлован|схема\s+котлован|планировочн\w+\s+организаци|коммуникаци\w+\s+схем',
        re.I | re.U,
    ), 'earthworks'),

    # waterproofing
    (re.compile(
        r'гидроизоляц|отсечная\s+гидро|вертикальная\s+гидро',
        re.I | re.U,
    ), 'waterproofing'),

    # walls / lintels — перемыч\w+ covers all case forms (перемычка, перемычек…)
    (re.compile(
        r'кладочный\s+план|план\s+этажа|перемыч\w+|армирование\s+кладк',
        re.I | re.U,
    ), 'load_bearing_walls_lintels'),

    # floor slab — explicit floor number FIRST (before generic "плит" catch-all)
    (re.compile(
        r'перекрытие\s+(?:над\s+)?1\s+этаж|плит\w+\s+перекрытия\s+(?:над\s+)?1\s+этаж'
        r'|над\s+1\s+этажом',
        re.I | re.U,
    ), 'floor_slab_1'),
    (re.compile(
        r'перекрытие\s+(?:над\s+)?2\s+этаж|плит\w+\s+перекрытия\s+(?:над\s+)?2\s+этаж'
        r'|над\s+2\s+этажом',
        re.I | re.U,
    ), 'floor_slab_2'),

    # floor slab — ambiguous: "армирование плиты" without "фундаментной"
    (re.compile(
        r'армирование\s+плит|плит\w+\s+перекрытия|перекрытие\s+плит',
        re.I | re.U,
    ), 'floor_slab_unknown'),
]

# ── Strong unique signals for header / row level ───────────────────────────────
# Only terms that are highly specific to one section and extremely unlikely to
# appear in tables from another section. Generic terms (газобетон, бетон,
# арматура) are intentionally excluded — they appear in multiple sections.

_STRONG_SIGNALS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'logicroof', re.I | re.U), 'flat_roof'),
    (re.compile(r'xps\s*slope|xps\s+экструд', re.I | re.U), 'flat_roof'),
    (re.compile(r'\bаэратор\b', re.I | re.U), 'flat_roof'),
    (re.compile(r'\bворонк\w+', re.I | re.U), 'flat_roof'),        # drain funnel
    (re.compile(r'schiedel', re.I | re.U), 'schiedel_vent_channels'),
    (re.compile(r'вентканал', re.I | re.U), 'schiedel_vent_channels'),
    (re.compile(r'термовставк\w*|термовставок', re.I | re.U), 'foundation_slab'),
    (re.compile(r'\bplanter\b', re.I | re.U), 'earthworks'),
]


# ── Public API ─────────────────────────────────────────────────────────────────

def infer_table_context_title(
    table: dict[str, Any],
    page: dict[str, Any],
    page_text_blocks: list[dict[str, Any]] | None = None,
) -> str:
    """Return the best available title for this table.

    Priority:
    1. table['table_title'] — if the PDF extractor populated it
    2. Nearest text block above the table (coordinate-based) — future
    3. Fallback: page['logical_sheet_title']
    """
    if table.get('table_title'):
        return table['table_title']
    if page_text_blocks:
        pass  # TODO: find nearest block above table by y-coordinate
    return page.get('logical_sheet_title', '')


def classify_table_section(
    table_context_title: str,
    table_headers: list[str],
    sample_rows: list[list[str]],
    page_section_code: str = '',
) -> dict[str, Any]:
    """Classify a table's construction section from its content.

    Returns:
      section_code        — classified section or '' if no signal found
      confidence          — 0.0–0.90
      source              — 'table_title' | 'table_headers' | 'table_rows' | 'none'
    """
    title_hay = _norm(table_context_title)
    headers_hay = _norm(_join(table_headers))
    rows_hay = _norm(_join(c for row in sample_rows[:3] for c in row))

    # 1. Title-level (0.90)
    for pattern, section in _TITLE_RULES:
        if pattern.search(title_hay):
            return {'section_code': section, 'confidence': 0.90, 'source': 'table_title'}

    # 2. Strong unique signal in headers (0.75)
    for pattern, section in _STRONG_SIGNALS:
        if pattern.search(headers_hay):
            return {'section_code': section, 'confidence': 0.75, 'source': 'table_headers'}

    # 3. Strong unique signal in first data rows (0.55)
    for pattern, section in _STRONG_SIGNALS:
        if pattern.search(rows_hay):
            return {'section_code': section, 'confidence': 0.55, 'source': 'table_rows'}

    return {'section_code': '', 'confidence': 0.0, 'source': 'none'}
