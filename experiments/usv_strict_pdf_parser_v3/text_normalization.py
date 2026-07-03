from __future__ import annotations

import re
from typing import Any


# ── Number pattern (Russian locale: comma as decimal separator) ────────────
_NUM = r'\d+(?:[.,]\d+)?'

# ── Generic Russian construction vocabulary word splits ────────────────────
# These handle terms that appear merged (no space) in PDF exports.
# ORDER MATTERS: longer/more specific patterns first.
# No project-specific values or filenames here.
_WORD_SPLITS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'Площадь\s*котлована', re.IGNORECASE | re.UNICODE), 'Площадь котлована'),
    (re.compile(r'Глубина\s*котлована', re.IGNORECASE | re.UNICODE), 'Глубина котлована'),
    (re.compile(r'Фундаментная\s*плита', re.IGNORECASE | re.UNICODE), 'Фундаментная плита'),
    (re.compile(r'Песчаное\s*основание', re.IGNORECASE | re.UNICODE), 'Песчаное основание'),
    (re.compile(r'Ливневая\s*канализация', re.IGNORECASE | re.UNICODE), 'Ливневая канализация'),
    (re.compile(r'Дренажная\s*система', re.IGNORECASE | re.UNICODE), 'Дренажная система'),
    (re.compile(r'ПНД\s*труба', re.IGNORECASE | re.UNICODE), 'ПНД труба'),
    (re.compile(r'Гофро?\s*труба', re.IGNORECASE | re.UNICODE), 'Гофро труба'),
    (re.compile(r'Ж/?Б\s*(?=плит)', re.IGNORECASE | re.UNICODE), 'Ж/Б '),
    # Word-immediately-before-digit splits (generic construction terms)
    (re.compile(r'\bЭППС(\d)', re.IGNORECASE | re.UNICODE), r'ЭППС \1'),
    (re.compile(r'\bПНД(\d)', re.IGNORECASE | re.UNICODE), r'ПНД \1'),
    (re.compile(r'\bТруба(\d)', re.IGNORECASE | re.UNICODE), r'Труба \1'),
    # Route label immediately before Cyrillic word (К1трасса → К1 трасса)
    # Standard Russian engineering network labels, not project-specific:
    # К1/К2/К3 = sewer/storm/drainage routes, В1 = water supply, ЭО = electrical route.
    (re.compile(r'\b([КВ])([0-9])([А-ЯЁа-яё])', re.UNICODE), r'\1\2 \3'),
]

# ── Diameter normalization ─────────────────────────────────────────────────
_DIAM_F = re.compile(r'\b[ФфF](\d+)', re.UNICODE)          # Ф110 → Ø110
_DIAM_D = re.compile(r'\b[Dd]=?\s*(\d+)', re.UNICODE)       # D110, d=110 → Ø110
_DIAM_OHM_SPACE = re.compile(r'[Øø]\s*(\d+)', re.UNICODE)  # Ø 110 → Ø110
_LETTER_BEFORE_OHM = re.compile(r'([А-ЯЁа-яёA-Za-z])\s*([Øø])', re.UNICODE)  # трубаØ → труба Ø

# ── Multiplication separator ───────────────────────────────────────────────
_MULT = re.compile(r'(\d)\s*[хxХ×]\s*(\d)', re.UNICODE)  # 300х300 → 300 × 300

# ── Merged number+unit patterns (no space between them) ───────────────────
# Applied in order of specificity: multi-char units before standalone м.
_MERGED_M2 = re.compile(
    rf'({_NUM})\s*(м²|м\^2|м\.?\s*кв\.?|кв\.?\s*м\.?|м2)',
    re.IGNORECASE | re.UNICODE,
)
_MERGED_M3 = re.compile(
    rf'({_NUM})\s*(м³|м\^3|м\.?\s*куб\.?|куб\.?\s*м\.?|м3)',
    re.IGNORECASE | re.UNICODE,
)
_MERGED_LIN = re.compile(
    rf'({_NUM})\s*(п(?:ог)?\.?\s*м\.?|м\.?\s*п\.?|м/п)',
    re.IGNORECASE | re.UNICODE,
)
_MERGED_MM = re.compile(
    rf'({_NUM})\s*(мм\.?|см\.?)',
    re.IGNORECASE | re.UNICODE,
)
# Standalone м: not followed by any word character (prevents matching м2, м3, мм, м/п)
_MERGED_M_ALONE = re.compile(rf'({_NUM})\s*(м)(?!\w)', re.UNICODE)
_MERGED_PCS = re.compile(
    rf'({_NUM})\s*(шт\.?|ед\.?|компл\.?)',
    re.IGNORECASE | re.UNICODE,
)

# ── Route label normalization ──────────────────────────────────────────────
# Standard Russian engineering network labels (not project-specific values):
# К1/К2/К3 = sewer/storm/drainage-related routes depending on project notation,
# В1 = water supply, ЭО = electrical equipment/electrical route.
# They are used as generic domain vocabulary for evidence/candidate detection.
_ROUTE = re.compile(r'\b([КкВв])\s*[-/]?\s*([0-9]+)\b', re.UNICODE)


def normalize_text(raw_text: str) -> str:
    """Return a cleaned copy of raw_text for search and candidate extraction.

    Never modifies raw_text – always returns a new string.
    Inserts spaces where construction PDF exports merge words/numbers/units.
    Does NOT add, remove or replace numeric values."""
    text = raw_text

    # 1. Apply building vocabulary splits (merged words)
    for pattern, replacement in _WORD_SPLITS:
        text = pattern.sub(replacement, text)

    # 2. Normalize diameter prefix (Ф110 → Ø110, D110 → Ø110)
    text = _DIAM_F.sub(r'Ø\1', text)
    text = _DIAM_D.sub(r'Ø\1', text)
    text = _DIAM_OHM_SPACE.sub(r'Ø\1', text)        # Ø 110 → Ø110
    text = _LETTER_BEFORE_OHM.sub(r'\1 \2', text)   # трубаØ → труба Ø

    # 3. Insert space between number and unit (order: longest units first)
    text = _MERGED_M2.sub(r'\1 \2', text)
    text = _MERGED_M3.sub(r'\1 \2', text)
    text = _MERGED_LIN.sub(r'\1 \2', text)
    text = _MERGED_MM.sub(r'\1 \2', text)
    text = _MERGED_M_ALONE.sub(r'\1 \2', text)
    text = _MERGED_PCS.sub(r'\1 \2', text)

    # 4. Normalize multiplication separator (300х300 → 300 × 300)
    text = _MULT.sub(r'\1 × \2', text)

    # 5. Normalize route labels (К-1 → К1, К 1 → К1, В-1 → В1)
    text = _ROUTE.sub(lambda m: m.group(1).upper() + m.group(2), text)

    # 6. Collapse multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


# ── Quantity parsing ───────────────────────────────────────────────────────

def _parse_decimal(raw: str) -> float:
    """Parse a number string with comma or dot as decimal separator."""
    return float(raw.replace(' ', '').replace(' ', '').replace(',', '.'))


def _length_canon(value: float, raw_unit: str) -> tuple[str, float, str]:
    """Return (normalized_unit, canonical_value_in_metres, 'm')."""
    u = raw_unit.lower().strip(' .')
    if 'мм' in u:
        return 'mm', round(value / 1000, 6), 'm'
    if 'см' in u:
        return 'cm', round(value / 100, 6), 'm'
    return 'm', round(value, 6), 'm'


def parse_quantities(text: str) -> list[dict[str, Any]]:
    """Extract structured quantity objects from text (raw or normalized).

    Returns one dict per quantity found. Multiple quantities per string
    are returned as separate items. Values are never invented or computed –
    only explicit numbers from the input text are returned.

    Note: some patterns may overlap for ambiguous unit strings (e.g. м in м/п).
    Callers should de-duplicate by span if precision matters.
    TODO: add span-based deduplication in a future iteration."""
    results: list[dict[str, Any]] = []

    # Diameter: Ø110, Ø110мм (after normalize_text has standardised the prefix)
    for m in re.finditer(
        r'[Øø](' + _NUM + r')\s*(мм\.?|см\.?|(?<!\w)м(?!\w))?',
        text, re.IGNORECASE | re.UNICODE,
    ):
        raw_val = m.group(1)
        raw_unit = (m.group(2) or 'мм').strip(' .')
        val = _parse_decimal(raw_val)
        norm_unit, canon_val, canon_unit = _length_canon(val, raw_unit)
        results.append({
            'kind': 'diameter',
            'raw': m.group(0).strip(),
            'raw_value': raw_val,
            'value_decimal': val,
            'raw_unit': raw_unit,
            'normalized_unit': norm_unit,
            'canonical_value': canon_val,
            'canonical_unit': canon_unit,
        })

    # Area (м2, м², кв.м, etc.)
    for m in re.finditer(
        rf'({_NUM})\s*(м²|м\^2|м\.?\s*кв\.?|кв\.?\s*м\.?|м\s*2|м2)',
        text, re.IGNORECASE | re.UNICODE,
    ):
        results.append({
            'kind': 'area',
            'raw': m.group(0).strip(),
            'raw_value': m.group(1),
            'value_decimal': _parse_decimal(m.group(1)),
            'raw_unit': m.group(2).strip(),
            'normalized_unit': 'm2',
        })

    # Volume (м3, м³, куб.м, etc.)
    for m in re.finditer(
        rf'({_NUM})\s*(м³|м\^3|м\.?\s*куб\.?|куб\.?\s*м\.?|м\s*3|м3)',
        text, re.IGNORECASE | re.UNICODE,
    ):
        results.append({
            'kind': 'volume',
            'raw': m.group(0).strip(),
            'raw_value': m.group(1),
            'value_decimal': _parse_decimal(m.group(1)),
            'raw_unit': m.group(2).strip(),
            'normalized_unit': 'm3',
        })

    # Linear metres (п.м, пог.м, м.п, м/п)
    for m in re.finditer(
        rf'({_NUM})\s*(п(?:ог)?\.?\s*м\.?|м\.?\s*п\.?|м/п)',
        text, re.IGNORECASE | re.UNICODE,
    ):
        results.append({
            'kind': 'linear_length',
            'raw': m.group(0).strip(),
            'raw_value': m.group(1),
            'value_decimal': _parse_decimal(m.group(1)),
            'raw_unit': m.group(2).strip(),
            'normalized_unit': 'linear_m',
        })

    # Length: мм, см, standalone м (not м2/м3/мм/м.п)
    for m in re.finditer(
        rf'({_NUM})\s*(мм\.?|см\.?|(?<![а-яёА-ЯЁ])м(?!\w))',
        text, re.IGNORECASE | re.UNICODE,
    ):
        raw_val = m.group(1)
        raw_unit = m.group(2).strip(' .')
        # skip if this looks like it's part of a larger unit already caught above
        if re.match(r'м[²³23]', m.group(2), re.UNICODE):
            continue
        val = _parse_decimal(raw_val)
        norm_unit, canon_val, canon_unit = _length_canon(val, raw_unit)
        results.append({
            'kind': 'length',
            'raw': m.group(0).strip(),
            'raw_value': raw_val,
            'value_decimal': val,
            'raw_unit': raw_unit,
            'normalized_unit': norm_unit,
            'canonical_value': canon_val,
            'canonical_unit': canon_unit,
        })

    # Pieces / units (шт, ед, компл)
    for m in re.finditer(
        rf'({_NUM})\s*(шт\.?|ед\.?|компл\.?)',
        text, re.IGNORECASE | re.UNICODE,
    ):
        results.append({
            'kind': 'quantity',
            'raw': m.group(0).strip(),
            'raw_value': m.group(1),
            'value_decimal': _parse_decimal(m.group(1)),
            'raw_unit': m.group(2).strip(' .'),
            'normalized_unit': 'pcs',
        })

    # Negative elevations / depths (-0,500, отм. -0,500, Глубина -0,5м)
    for m in re.finditer(
        r'(?:отм\.?\s*|отметк[аи]?\s*)?[-−–—]\s*(\d+[.,]\d+)\s*(м\.?)?',
        text, re.UNICODE,
    ):
        raw_val = m.group(1)
        results.append({
            'kind': 'elevation',
            'raw': m.group(0).strip(),
            'raw_value': raw_val,
            'value_decimal': -_parse_decimal(raw_val),
            'raw_unit': 'м',
            'normalized_unit': 'm',
            'sign': 'negative',
        })

    # Positive elevations (+0,000, отм. +3,750)
    for m in re.finditer(
        r'(?:отм\.?\s*|отметк[аи]?\s*)?\+\s*(\d+[.,]\d+)\s*(м\.?)?',
        text, re.UNICODE,
    ):
        raw_val = m.group(1)
        results.append({
            'kind': 'elevation',
            'raw': m.group(0).strip(),
            'raw_value': raw_val,
            'value_decimal': _parse_decimal(raw_val),
            'raw_unit': 'м',
            'normalized_unit': 'm',
            'sign': 'positive',
        })

    # Dimensions (300 × 300 × 300, only reliable after normalize_text produces ×)
    for m in re.finditer(
        r'(\d+)\s*×\s*(\d+)(?:\s*×\s*(\d+))?\s*(мм\.?|см\.?|м\.?)?',
        text, re.UNICODE,
    ):
        parts = [int(m.group(1)), int(m.group(2))]
        if m.group(3):
            parts.append(int(m.group(3)))
        raw_unit = (m.group(4) or '').strip(' .')
        results.append({
            'kind': 'dimensions',
            'raw': m.group(0).strip(),
            'values': parts,
            'raw_unit': raw_unit or None,
            'normalized_unit': (
                'mm' if raw_unit and 'мм' in raw_unit.lower()
                else 'cm' if raw_unit and 'см' in raw_unit.lower()
                else 'm' if raw_unit
                else None
            ),
        })

    return results
