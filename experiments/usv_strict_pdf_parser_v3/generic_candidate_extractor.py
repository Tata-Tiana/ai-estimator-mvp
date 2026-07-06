from __future__ import annotations

import json
import re
from typing import Any

import parser_paths
from construction_vocabulary import MATERIALS_RE, SUBJECTS_RE
from text_normalization import normalize_text, parse_quantities


# ── Standard Russian engineering domain vocabulary ─────────────────────────
# These are generic construction terms used as semantic signals for candidate
# detection. They are NOT project-specific values, filenames, or page numbers.

# Unambiguous route-label vocabulary: full descriptive words that cannot mean
# anything else in a construction PDF. No extra context required.
_ROUTE_LABEL_WORD = re.compile(
    r'\b('
    r'Дренаж\w*'                   # Дренаж, Дренажная…
    r'|Др\.?'                        # Др. short form
    r'|Ливнев\w+'                   # Ливневка, Ливневая…
    r'|Канализаци\w+'               # Канализация…
    r'|Водоснабжен\w+'              # Водоснабжение…
    r'|Эл\.?\s*кабел\w*'            # Эл. кабель, Эл.кабель
    r'|Электрическ\w+\s+кабел\w*'  # Электрический кабель
    r')\b',
    re.IGNORECASE | re.UNICODE,
)

# Ambiguous short-code route labels (A4.2.7): К1/К2/К3 = sewer/storm/drainage
# routes, В1 = water supply, ЭО = electrical route, ЛК = abbreviation. These
# codes collide with unrelated numbering schemes on the same PDFs — most
# notably АР door/window opening marks (ОК-1, ДН-1, ДВ-1, "В-1" as an opening
# code). They only count as route labels when engineering context is present
# nearby (see _match_route_label) and never next to opening-schedule context.
# IGNORECASE is safe here because К/В require a trailing digit (К1, В1…),
# so bare lowercase к/в (Russian prepositions) cannot match.
_ROUTE_LABEL_CODE = re.compile(
    r'\b('
    r'К[0-9]+'                      # К1, К2, К3 — digit required
    r'|В[0-9]+(?![.,][0-9])'         # В1, В2 route labels — not В22,5 concrete class
    r'|ЭО[0-9]?'                    # ЭО, ЭО1 — digit optional
    r'|ЛК'                           # ЛК abbreviation
    r')\b',
    re.IGNORECASE | re.UNICODE,
)

# Engineering context required for ambiguous short codes (A4.2.7).
_ROUTE_ENGINEERING_CONTEXT_RE = re.compile(
    r'трасса|канализаци|водоснабжен|ливнев|дренаж|труб|ввод|'
    r'инженерные сети|коммуникаци',
    re.IGNORECASE | re.UNICODE,
)

# АР (architectural) opening-schedule context that must suppress a route
# label match regardless of engineering context elsewhere on the same row
# (A4.2.7): door/window opening marks and their schedules reuse short
# alphanumeric codes that otherwise look like route labels.
_AR_OPENING_CONTEXT_RE = re.compile(
    r'ведомость дверных|ведомость оконных|габариты проемов|фасад|'
    r'\bок-|\bдн-|\bдв-',
    re.IGNORECASE | re.UNICODE,
)

_ITOGO = re.compile(r'\bитого\b', re.IGNORECASE | re.UNICODE)

_EARTHWORKS_KW = re.compile(
    r'котлован|яма|выемк|подготовк',
    re.IGNORECASE | re.UNICODE,
)
_DEPTH_KW = re.compile(
    r'глубин|отметк|ур\.?\s*земл|уровн',
    re.IGNORECASE | re.UNICODE,
)
_AREA_KW = re.compile(r'площадь|площад', re.IGNORECASE | re.UNICODE)
_LENGTH_KW = re.compile(r'длин|протяжен|трасс', re.IGNORECASE | re.UNICODE)
_VOLUME_KW = re.compile(r'объ[её]м|v\s*=', re.IGNORECASE | re.UNICODE)
_WIDTH_KW = re.compile(r'ширин', re.IGNORECASE | re.UNICODE)

_MATERIAL_KW = MATERIALS_RE
_PIPE_KW = re.compile(
    r'труб|ПНД|ПВХ|гофр|трубопровод',
    re.IGNORECASE | re.UNICODE,
)
_PIPE_FITTING_KW = re.compile(
    r'колен|муфт|тройник|дождеприём|дождеприем|ревизи|угол|переход',
    re.IGNORECASE | re.UNICODE,
)
# Any keyword suggesting an engineering subject
_ANY_SUBJECT_KW = SUBJECTS_RE

# Label–value separator pattern for label_value_quantity detection
_LABEL_SEP_VALUE = re.compile(
    r'(?P<label>[А-ЯЁа-яёA-Za-z][А-ЯЁа-яё\s/]{2,40}?)\s*'
    r'(?P<sep>[-–—:=])\s*'
    r'(?P<value>\d+(?:[.,]\d+)?)\s*'
    r'(?P<unit>м²|м³|м\^2|м\^3|кв\.?\s*м\.?|м\.?\s*кв\.?|куб\.?\s*м\.?|м\.?\s*куб\.?'
    r'|п(?:ог)?\.?\s*м\.?|м\.?\s*п\.?|м/п|мм\.?|см\.?|м2|м3|шт\.?|ед\.?|компл\.?|кг\.?'
    r'|(?<!\w)м(?!\w))',
    re.IGNORECASE | re.UNICODE,
)


def _all_elevation(quantities: list[dict[str, Any]]) -> bool:
    """True when every parsed quantity is an elevation marker (kind='elevation')."""
    return bool(quantities) and all(q.get('kind') == 'elevation' for q in quantities)


def _has_useful_primary_quantity(value_candidates: list[dict[str, Any]]) -> bool:
    """True when at least one value is usable as a primary route quantity.

    Excludes diameter, elevation, and bare millimetre size measurements.
    A 'length' kind with unit 'mm'/'мм' is typically a diameter attribute
    (Ø110 мм) parsed redundantly alongside the diameter kind — not a route qty.

    IMPORTANT (A4.2.7 fix): must be called with the *post-filter*
    value_candidates (i.e. after _value_candidates_from_quantities), not the
    raw parse_quantities() output. Raw quantities can include kind='dimensions'
    entries (e.g. "90х195") that satisfy this predicate but then get dropped
    by _value_candidates_from_quantities — leaving a candidate that passed
    the gate with no genuinely useful value stored at all.
    """
    return any(
        q.get('kind') not in ('diameter', 'elevation')
        and q.get('normalized_unit') not in ('mm', 'мм')
        for q in value_candidates
    )


def _match_route_label(norm: str, ev: dict[str, Any]) -> re.Match[str] | None:
    """Route label detection with context guards (A4.2.7).

    Unambiguous full words (Дренаж, Канализация, Водоснабжение…) match with no
    extra context — they cannot mean anything else.

    Ambiguous short codes (К1, В1, ЭО, ЛК) only count as route labels when
    engineering context (трасса/канализация/водоснабжение/дренаж/труба/ввод/
    инженерные сети/коммуникации — or an already-established length/depth/
    volume/area/итого signal) is present on the same row/page text. They never
    count next to an АР opening-schedule context (ведомость дверных/оконных
    проемов, габариты проемов, фасад, ОК-/ДН-/ДВ- codes), which reuses the
    same short alphanumeric shape for door/window marks.
    """
    ar_context = ' '.join(filter(None, [
        norm, ev.get('table_context_title', ''), ev.get('logical_sheet_title', ''),
    ]))
    if _AR_OPENING_CONTEXT_RE.search(ar_context):
        return None

    word_match = _ROUTE_LABEL_WORD.search(norm)
    if word_match:
        return word_match

    code_match = _ROUTE_LABEL_CODE.search(norm)
    if code_match and (
        _ROUTE_ENGINEERING_CONTEXT_RE.search(norm)
        or _ITOGO.search(norm)
        or _LENGTH_KW.search(norm)
        or _DEPTH_KW.search(norm)
        or _VOLUME_KW.search(norm)
        or _AREA_KW.search(norm)
    ):
        return code_match
    return None


def _has_any_quantity(text: str) -> bool:
    return bool(re.search(
        r'\d+(?:[.,]\d+)?\s*(?:м²|м³|м\^2|м\^3|м2|м3|п\.?\s*м|пог\.?\s*м|м\.?\s*п'
        r'|мм|см|шт|ед|компл|кг|(?<!\w)м(?!\w))',
        text, re.IGNORECASE | re.UNICODE,
    ))


def _property_hint_from_text(text: str) -> str:
    t = text.lower()
    if _DEPTH_KW.search(t):
        return 'depth'
    if _AREA_KW.search(t):
        return 'area'
    if _LENGTH_KW.search(t):
        return 'length'
    if _VOLUME_KW.search(t):
        return 'volume'
    if _WIDTH_KW.search(t):
        return 'width'
    return 'quantity'


def _value_candidates_from_quantities(quantities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for q in quantities:
        if q.get('kind') == 'dimensions':
            continue  # dimensions are not simple scalar candidates
        result.append({
            'raw_value': q.get('raw_value') or q.get('raw', ''),
            'value_decimal': q.get('value_decimal'),
            'raw_unit': q.get('raw_unit', ''),
            'normalized_unit': q.get('normalized_unit', ''),
            'kind': q.get('kind', ''),
            'canonical_value': q.get('canonical_value'),
            'canonical_unit': q.get('canonical_unit'),
            'source': 'evidence_text',
        })
    return result


def _make_elevation_marker(
    ev: dict[str, Any],
    cand_id: int,
    quantities: list[dict[str, Any]],
    raw: str,
    norm: str,
    src: dict[str, Any],
) -> dict[str, Any]:
    """Elevation values (+3,250, -0,300) stored as markers, not ordinary quantities.

    Resolver ignores these unless the parameter explicitly expects kind=elevation.
    """
    return {
        'candidate_id': f'cand_{cand_id:06d}',
        'candidate_type': 'elevation_marker',
        'subject_hint': '',
        'property_hint': 'elevation',
        'value_candidates': _value_candidates_from_quantities(quantities),
        'unit_candidates': [],
        'evidence_id': ev['evidence_id'],
        'raw_text': raw,
        'normalized_text': norm,
        'confidence': 0.20,
        'reason': 'elevation-only values — not an ordinary quantity',
        'extractor': 'generic_candidate_extractor',
        **src,
    }


def _make_diameter_spec(
    ev: dict[str, Any],
    cand_id: int,
    quantities: list[dict[str, Any]],
    raw: str,
    norm: str,
    src: dict[str, Any],
) -> dict[str, Any]:
    """Diameter-only values (Ø110, ф315) stored as diameter_spec attributes.

    Not usable as primary length/volume candidates by the resolver.
    """
    return {
        'candidate_id': f'cand_{cand_id:06d}',
        'candidate_type': 'diameter_spec',
        'subject_hint': '',
        'property_hint': 'diameter',
        'value_candidates': _value_candidates_from_quantities(quantities),
        'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
        'evidence_id': ev['evidence_id'],
        'raw_text': raw,
        'normalized_text': norm,
        'confidence': 0.25,
        'reason': 'diameter-only — not a useful primary quantity',
        'extractor': 'generic_candidate_extractor',
        **src,
    }


def _ev_source_fields(ev: dict[str, Any]) -> dict[str, Any]:
    """Extract section/page provenance fields from an evidence item."""
    return {
        'section_code': ev.get('section_code', 'unknown'),
        'page_section_code': ev.get('page_section_code', 'unknown'),
        'section_confidence': ev.get('section_confidence', 0.0),
        'section_source': ev.get('section_source', 'unknown'),
        'table_section_code': ev.get('table_section_code', ''),
        'table_section_confidence': ev.get('table_section_confidence', 0.0),
        'table_section_source': ev.get('table_section_source', 'none'),
        'logical_sheet_title': ev.get('logical_sheet_title', ''),
        'logical_sheet_type': ev.get('logical_sheet_type', 'unknown'),
        'table_context_title': ev.get('table_context_title', ''),
        'source_pdf': ev.get('source_pdf', ''),
        'physical_page_number': ev.get('physical_page_number'),
        'table_index': ev.get('table_index'),
        'row_index': ev.get('row_index'),
    }


def _classify_evidence(
    ev: dict[str, Any],
    cand_id: int,
) -> dict[str, Any] | None:
    """Attempt to classify one evidence item into a candidate.

    Returns a candidate dict or None if the evidence is not relevant."""
    norm = ev.get('normalized_text') or normalize_text(ev.get('raw_text', ''))
    raw = ev.get('raw_text', '')
    src = _ev_source_fields(ev)

    # For table_row evidence the cells are joined with " | " by evidence_layer,
    # so "150 | м2" doesn't match adjacent number+unit patterns.  Strip pipes
    # before quantity parsing; normalized_text in the candidate still keeps them.
    qty_text = re.sub(r'\s*\|\s*', ' ', norm) if ev.get('source_kind') == 'table_row' else norm
    quantities = parse_quantities(qty_text)
    has_qty = bool(quantities)

    # Elevation-only values must be checked before the main gate because elevation
    # text (e.g. "+3,250") has no unit suffix, so _has_any_quantity() would miss it.
    if _all_elevation(quantities):
        return _make_elevation_marker(ev, cand_id, quantities, raw, norm, src)

    if not _has_any_quantity(norm) and not _ANY_SUBJECT_KW.search(norm):
        return None

    # ── 1. route_summary: route label + ИТОГО or length/volume/depth keywords ──
    route_match = _match_route_label(norm, ev)
    if route_match and has_qty:
        # Elevation-only: store as marker, not a useful route quantity
        if _all_elevation(quantities):
            return _make_elevation_marker(ev, cand_id, quantities, raw, norm, src)
        value_candidates = _value_candidates_from_quantities(quantities)
        # Diameter-only (or only-dimensions-then-filtered): no useful primary
        # quantity actually survives → store as diameter_spec (A4.2.7 fix:
        # check the post-filter value_candidates, not raw quantities).
        if not _has_useful_primary_quantity(value_candidates):
            return _make_diameter_spec(ev, cand_id, quantities, raw, norm, src)

        subject = route_match.group(0).strip()
        confidence = 0.85 if _ITOGO.search(norm) else 0.70
        prop = _property_hint_from_text(norm)
        reason_parts = ['route label found']
        if _ITOGO.search(norm):
            reason_parts.append('ИТОГО keyword')
        if _LENGTH_KW.search(norm):
            reason_parts.append('length keyword')
        if _VOLUME_KW.search(norm):
            reason_parts.append('volume keyword')
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'route_summary',
            'subject_hint': subject,
            'property_hint': prop,
            'value_candidates': value_candidates,
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': confidence,
            'reason': '; '.join(reason_parts),
            'extractor': 'generic_candidate_extractor',
            **src,
        }

    # ── 2. pipe_item: pipe keyword + length unit ───────────────────────────
    if _PIPE_KW.search(norm) and has_qty:
        value_candidates = _value_candidates_from_quantities(quantities)
        # Diameter-only ("Труба Ø110 мм" without п.м or шт) → not a usable pipe
        # qty. A4.2.7 fix: check post-filter value_candidates, not raw quantities.
        if not _has_useful_primary_quantity(value_candidates):
            return _make_diameter_spec(ev, cand_id, quantities, raw, norm, src)
        pipe_match = _PIPE_KW.search(norm)
        subject_parts = []
        if pipe_match:
            # include Ø/diameter info if present
            diam_match = re.search(r'[Øø]\d+', norm)
            subject_parts.append(norm[pipe_match.start():pipe_match.end() + 20].split()[0])
            if diam_match:
                subject_parts.append(diam_match.group(0))
        subject = ' '.join(subject_parts).strip()
        linear_qtys = [q for q in value_candidates if q.get('normalized_unit') == 'linear_m']
        confidence = 0.85 if linear_qtys else 0.65
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'pipe_item',
            'subject_hint': subject,
            'property_hint': 'length',
            'value_candidates': value_candidates,
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': confidence,
            'reason': 'pipe keyword + quantity',
            'extractor': 'generic_candidate_extractor',
            **src,
        }

    # ── 3. pipe_piece_qty: pipe fitting keywords + quantity ────────────────
    if _PIPE_FITTING_KW.search(norm) and has_qty:
        fit_match = _PIPE_FITTING_KW.search(norm)
        subject = norm[fit_match.start():fit_match.end() + 15].split()[0] if fit_match else ''
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'pipe_piece_qty',
            'subject_hint': subject,
            'property_hint': 'quantity',
            'value_candidates': _value_candidates_from_quantities(quantities),
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': 0.75,
            'reason': 'pipe fitting keyword + quantity',
            'extractor': 'generic_candidate_extractor',
            **src,
        }

    # ── 4. label_value_quantity: "Label - value unit" ─────────────────────
    lv_match = _LABEL_SEP_VALUE.search(norm)
    if lv_match:
        label = lv_match.group('label').strip()
        prop = _property_hint_from_text(label)
        if _EARTHWORKS_KW.search(label) or _DEPTH_KW.search(label) or _AREA_KW.search(label):
            confidence = 0.82
        elif _ANY_SUBJECT_KW.search(label):
            confidence = 0.70
        else:
            confidence = 0.55
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'label_value_quantity',
            'subject_hint': label,
            'property_hint': prop,
            'value_candidates': _value_candidates_from_quantities(quantities),
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': confidence,
            'reason': f'label "{label}" + separator + value+unit',
            'extractor': 'generic_candidate_extractor',
            **src,
        }

    # ── 5. material_quantity: material keyword + any quantity ──────────────
    if _MATERIAL_KW.search(norm) and has_qty:
        value_candidates = _value_candidates_from_quantities(quantities)
        # A4.2.7 fix: if nothing useful survives filtering (only
        # diameter/elevation/bare-mm entries remain, e.g. dimensions like
        # "90х195" got dropped), this is not a resolver-eligible material
        # quantity. No natural fallback type exists for material_quantity
        # (unlike route_summary/pipe_item → diameter_spec), so drop it.
        if not _has_useful_primary_quantity(value_candidates):
            return None
        mat_match = _MATERIAL_KW.search(norm)
        subject = norm[mat_match.start():mat_match.end() + 20].split()[0] if mat_match else ''
        prop = _property_hint_from_text(norm)
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'material_quantity',
            'subject_hint': subject,
            'property_hint': prop,
            'value_candidates': value_candidates,
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': 0.75,
            'reason': 'material keyword + quantity',
            'extractor': 'generic_candidate_extractor',
            **src,
        }

    # ── 6. table_quantity_row: table row with engineering subject + quantity ─
    if ev.get('source_kind') == 'table_row' and _ANY_SUBJECT_KW.search(norm) and has_qty:
        prop = _property_hint_from_text(norm)
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'table_quantity_row',
            'subject_hint': '',
            'property_hint': prop,
            'value_candidates': _value_candidates_from_quantities(quantities),
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': 0.55,
            'reason': 'table row: engineering keyword + quantity',
            'extractor': 'generic_candidate_extractor',
            **src,
        }

    # ── 7. unknown_relevant_quantity: catch-all for relevant strings ────────
    if _ANY_SUBJECT_KW.search(norm) and has_qty:
        # Elevation-only values are markers, not ordinary quantities
        if _all_elevation(quantities):
            return _make_elevation_marker(ev, cand_id, quantities, raw, norm, src)
        prop = _property_hint_from_text(norm)
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'unknown_relevant_quantity',
            'subject_hint': '',
            'property_hint': prop,
            'value_candidates': _value_candidates_from_quantities(quantities),
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': 0.35,
            'reason': 'engineering keyword + quantity, type unclear',
            'extractor': 'generic_candidate_extractor',
            **src,
        }

    return None


def _extract_candidates_from_evidence(
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build generic candidates from a pre-loaded evidence list.

    Separated from extract_generic_candidates() so tests can pass synthetic data
    without touching the filesystem."""
    candidates: list[dict[str, Any]] = []
    cand_id = 0
    for ev in evidence:
        cand_id += 1
        result = _classify_evidence(ev, cand_id)
        if result is not None:
            candidates.append(result)
    return candidates


def extract_generic_candidates() -> list[dict[str, Any]]:
    """Read evidence.json and produce generic_candidates.json.

    Works on any project – uses semantic signals only, no project-specific
    filenames, page numbers, or hardcoded values."""
    ev_path = parser_paths.evidence_path()
    if not ev_path.exists():
        return []

    evidence: list[dict[str, Any]] = json.loads(ev_path.read_text(encoding='utf-8'))
    candidates = _extract_candidates_from_evidence(evidence)

    dest = parser_paths.generic_candidates_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return candidates


def main() -> int:
    cands = extract_generic_candidates()
    print(f'generic_candidates: {parser_paths.generic_candidates_path()} ({len(cands)} items)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
