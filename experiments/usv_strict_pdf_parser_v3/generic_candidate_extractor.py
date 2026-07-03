from __future__ import annotations

import json
import re
from typing import Any

import parser_paths
from text_normalization import normalize_text, parse_quantities


# ── Standard Russian engineering domain vocabulary ─────────────────────────
# These are generic construction terms used as semantic signals for candidate
# detection. They are NOT project-specific values, filenames, or page numbers.

# Standard Russian engineering network labels (not project-specific values):
# К1/К2/К3 = sewer/storm/drainage-related routes depending on project notation,
# В1 = water supply, ЭО = electrical equipment/electrical route.
# They are used as generic domain vocabulary for evidence/candidate detection.
_ROUTE_LABEL = re.compile(
    r'\b(К[0-9]?|В[0-9]?|ЭО[0-9]?|Дренаж|Др\.?|ЛК)\b',
    re.UNICODE | re.IGNORECASE,
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

_MATERIAL_KW = re.compile(
    r'песок|геотекстил|щебен|ЭППС|Плантер|мембран|гидроизол|рубемаст|утеплит|пенопол',
    re.IGNORECASE | re.UNICODE,
)
_PIPE_KW = re.compile(
    r'труб|ПНД|ПВХ|гофр|трубопровод',
    re.IGNORECASE | re.UNICODE,
)
_PIPE_FITTING_KW = re.compile(
    r'колен|муфт|тройник|дождеприём|дождеприем|ревизи|угол|переход',
    re.IGNORECASE | re.UNICODE,
)
# Any keyword suggesting an engineering subject
_ANY_SUBJECT_KW = re.compile(
    r'котлован|яма|выемк|глубин|площадь|площад|траншей|трасс|труб|ПНД|ПВХ|гофр'
    r'|песок|геотекстил|щебен|ЭППС|Плантер|мембран|колен|муфт|тройник|дождеприём'
    r'|дождеприем|ревизи|длин|объ[её]м|ширин|глубин|итого|К[0-9]|В[0-9]|ЭО',
    re.IGNORECASE | re.UNICODE,
)

# Label–value separator pattern for label_value_quantity detection
_LABEL_SEP_VALUE = re.compile(
    r'(?P<label>[А-ЯЁа-яёA-Za-z][А-ЯЁа-яё\s/]{2,40}?)\s*'
    r'(?P<sep>[-–—:=])\s*'
    r'(?P<value>\d+(?:[.,]\d+)?)\s*'
    r'(?P<unit>м²|м³|м\^2|м\^3|кв\.?\s*м\.?|м\.?\s*кв\.?|куб\.?\s*м\.?|м\.?\s*куб\.?'
    r'|п(?:ог)?\.?\s*м\.?|м\.?\s*п\.?|м/п|мм\.?|см\.?|м2|м3|шт\.?|ед\.?|компл\.?'
    r'|(?<!\w)м(?!\w))',
    re.IGNORECASE | re.UNICODE,
)


def _has_any_quantity(text: str) -> bool:
    return bool(re.search(
        r'\d+(?:[.,]\d+)?\s*(?:м²|м³|м\^2|м\^3|м2|м3|п\.?\s*м|пог\.?\s*м|м\.?\s*п'
        r'|мм|см|шт|ед|компл|(?<!\w)м(?!\w))',
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
            'canonical_value': q.get('canonical_value'),
            'canonical_unit': q.get('canonical_unit'),
            'source': 'evidence_text',
        })
    return result


def _classify_evidence(
    ev: dict[str, Any],
    cand_id: int,
) -> dict[str, Any] | None:
    """Attempt to classify one evidence item into a candidate.

    Returns a candidate dict or None if the evidence is not relevant."""
    norm = ev.get('normalized_text') or normalize_text(ev.get('raw_text', ''))
    raw = ev.get('raw_text', '')

    if not _has_any_quantity(norm) and not _ANY_SUBJECT_KW.search(norm):
        return None

    # For table_row evidence the cells are joined with " | " by evidence_layer,
    # so "150 | м2" doesn't match adjacent number+unit patterns.  Strip pipes
    # before quantity parsing; normalized_text in the candidate still keeps them.
    qty_text = re.sub(r'\s*\|\s*', ' ', norm) if ev.get('source_kind') == 'table_row' else norm
    quantities = parse_quantities(qty_text)
    has_qty = bool(quantities)

    # ── 1. route_summary: route label + ИТОГО or length/volume/depth keywords ──
    if _ROUTE_LABEL.search(norm) and has_qty:
        route_match = _ROUTE_LABEL.search(norm)
        subject = (route_match.group(0) if route_match else '').strip()
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
            'value_candidates': _value_candidates_from_quantities(quantities),
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': confidence,
            'reason': '; '.join(reason_parts),
            'extractor': 'generic_candidate_extractor',
        }

    # ── 2. pipe_item: pipe keyword + length unit ───────────────────────────
    if _PIPE_KW.search(norm) and has_qty:
        pipe_match = _PIPE_KW.search(norm)
        subject_parts = []
        if pipe_match:
            # include Ø/diameter info if present
            diam_match = re.search(r'[Øø]\d+', norm)
            subject_parts.append(norm[pipe_match.start():pipe_match.end() + 20].split()[0])
            if diam_match:
                subject_parts.append(diam_match.group(0))
        subject = ' '.join(subject_parts).strip()
        linear_qtys = [q for q in quantities if q.get('normalized_unit') == 'linear_m']
        confidence = 0.85 if linear_qtys else 0.65
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'pipe_item',
            'subject_hint': subject,
            'property_hint': 'length',
            'value_candidates': _value_candidates_from_quantities(quantities),
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': confidence,
            'reason': 'pipe keyword + quantity',
            'extractor': 'generic_candidate_extractor',
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
        }

    # ── 5. material_quantity: material keyword + any quantity ──────────────
    if _MATERIAL_KW.search(norm) and has_qty:
        mat_match = _MATERIAL_KW.search(norm)
        subject = norm[mat_match.start():mat_match.end() + 20].split()[0] if mat_match else ''
        prop = _property_hint_from_text(norm)
        return {
            'candidate_id': f'cand_{cand_id:06d}',
            'candidate_type': 'material_quantity',
            'subject_hint': subject,
            'property_hint': prop,
            'value_candidates': _value_candidates_from_quantities(quantities),
            'unit_candidates': list({q.get('normalized_unit', '') for q in quantities if q.get('normalized_unit')}),
            'evidence_id': ev['evidence_id'],
            'raw_text': raw,
            'normalized_text': norm,
            'confidence': 0.75,
            'reason': 'material keyword + quantity',
            'extractor': 'generic_candidate_extractor',
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
        }

    # ── 7. unknown_relevant_quantity: catch-all for relevant strings ────────
    if _ANY_SUBJECT_KW.search(norm) and has_qty:
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
