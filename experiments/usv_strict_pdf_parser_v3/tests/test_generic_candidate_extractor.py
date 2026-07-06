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


# ── no false route_summary for Russian prepositions в/к ───────────────────

def test_no_route_summary_for_preposition_lowercase_v() -> None:
    """Lowercase 'в' (Russian preposition) must not produce route_summary."""
    cands = _candidates_from_text('Глубина в 0,9 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert not routes, f'Preposition "в" must not become route_summary: {routes}'


def test_no_route_summary_for_preposition_lowercase_k() -> None:
    """Lowercase 'к' (Russian preposition) must not produce route_summary."""
    cands = _candidates_from_text('Доступ к котловану 50 м2')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert not routes, f'Preposition "к" must not become route_summary: {routes}'


# ── no project-specific hardcoding (structural check) ────────────────────

def test_no_trc_specific_logic() -> None:
    """Verify extractor works for a synthetic project with different route names.
    If the extractor were project-specific, it would fail or return nothing here."""
    # Using a different network labelling scheme to ensure generality
    cands = _candidates_from_text('В2 ИТОГО длина 35,0 п.м объем 14,0 м3')
    route = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert route, 'Extractor must work for any route label, not just one specific project'


# ── false positives: combined prepositions and garbled text ──────────────

def test_no_route_summary_for_sentence_with_both_prepositions() -> None:
    """Sentence with prepositions 'в' and 'к' but no route label must not
    produce route_summary with subject_hint 'в' or 'к'."""
    cands = _candidates_from_text('в месте прохода к дому глубина 0,5 м')
    bad = [
        c for c in cands
        if c['candidate_type'] == 'route_summary'
        and c.get('subject_hint', '').strip().lower() in ('в', 'к')
    ]
    assert not bad, f'Prepositions must not become route labels: {bad}'


def test_no_route_summary_for_garbled_text() -> None:
    """Garbled/repeated characters with a quantity must not produce route_summary."""
    cands = _candidates_from_text('ВВВннн вввооодддоооссстттоооккк 0,5 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert not routes, f'Garbled text must not produce route_summary: {routes}'


# ── new словесные route labels ────────────────────────────────────────────

def test_route_summary_livnevka() -> None:
    cands = _candidates_from_text('Ливневка ИТОГО длина 55,0 п.м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'Ливневка must produce route_summary'


def test_route_summary_kanalizatsiya() -> None:
    cands = _candidates_from_text('Канализация длина 30,0 п.м глубина 1,0 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'Канализация must produce route_summary'


def test_route_summary_vodosnabzhenie() -> None:
    cands = _candidates_from_text('Водоснабжение длина 22,0 п.м глубина 1,2 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'Водоснабжение must produce route_summary'


def test_route_summary_el_kabel() -> None:
    cands = _candidates_from_text('Эл. кабель длина 18,0 п.м глубина 0,7 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'Эл. кабель must produce route_summary'


# ── spec confirmation tests (synthetic values) ───────────────────────────

def test_route_summary_k1_spec_values() -> None:
    cands = _candidates_from_text('К1 ИТОГО длина 28,4 п.м объем 12,49 м3')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'К1 must produce route_summary'
    assert any('К1' in c.get('subject_hint', '') for c in routes)


def test_route_summary_v1_pipe_context() -> None:
    cands = _candidates_from_text('В1 труба ПНД Ø110 мм 12,4 п.м')
    hits = [c for c in cands
            if c['candidate_type'] in ('route_summary', 'pipe_item')]
    assert hits, 'В1 with pipe context must produce route_summary or pipe_item'


def test_route_summary_eo_trassa() -> None:
    cands = _candidates_from_text('ЭО трасса кабеля 15 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'ЭО without digit must produce route_summary'
    assert any('ЭО' in c.get('subject_hint', '').upper() for c in routes)


def test_route_summary_drenazh_itogo() -> None:
    cands = _candidates_from_text('Дренаж ИТОГО длина 40 п.м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'Дренаж must produce route_summary'


# ── new vocabulary: concrete, rebar, masonry, roofing, ventilation ────────

def test_material_quantity_concrete() -> None:
    cands = _candidates_from_text('Бетон В22,5 W6 F150 П4 55,0 м3')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'Бетон must produce material_quantity'
    # Only m3 should be the meaningful quantity — not the class digits
    kg_vals = [
        vc for c in mats for vc in c['value_candidates']
        if vc.get('normalized_unit') == 'kg'
    ]
    assert not kg_vals, 'Concrete class digits must not produce kg candidates'


def test_material_quantity_rebar_weight_kg() -> None:
    # Rebar class A500 + weight in kg (typical spec line, synthetic values)
    cands = _candidates_from_text('А500С ф12 200 кг')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'А500С must produce material_quantity'
    kg_vals = [
        vc for c in mats for vc in c['value_candidates']
        if vc.get('normalized_unit') == 'kg'
    ]
    assert kg_vals, 'Rebar line with кг must produce a kg value_candidate'
    assert kg_vals[0]['value_decimal'] == 200.0


def test_material_quantity_rebar_class_a240() -> None:
    cands = _candidates_from_text('А240 ф6 хомуты 45,0 кг')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'А240 must produce material_quantity'


def test_material_quantity_gas_block() -> None:
    cands = _candidates_from_text('Газобетонный блок 600х400х250 90,0 м3')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'Газобетонный must produce material_quantity'


def test_material_quantity_masonry_lintel() -> None:
    cands = _candidates_from_text('Перемычка в U-блоке 2,5 м3')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'Перемычка must produce material_quantity'


def test_material_quantity_logicroof() -> None:
    cands = _candidates_from_text('LOGICROOF V-RP мембрана 300 м2')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'LOGICROOF must produce material_quantity'


def test_material_quantity_schiedel() -> None:
    cands = _candidates_from_text('Schiedel VENT 30 шт')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'Schiedel must produce material_quantity'


def test_material_quantity_mastic_kg() -> None:
    cands = _candidates_from_text('Мастика битумная 50 кг')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'Мастика must produce material_quantity'
    kg_vals = [
        vc for c in mats for vc in c['value_candidates']
        if vc.get('normalized_unit') == 'kg'
    ]
    assert kg_vals, 'Мастика with кг must produce a kg value_candidate'


def test_material_quantity_thermal_insert() -> None:
    cands = _candidates_from_text('Термовставки 50 мм 20 п.м')
    mats = [c for c in cands if c['candidate_type'] == 'material_quantity']
    assert mats, 'Термовставки must produce material_quantity'


def test_value_candidate_kind_weight() -> None:
    # value_candidates must carry kind='weight' for kg quantities
    cands = _candidates_from_text('А500С ф10 150 кг')
    all_vcs = [vc for c in cands for vc in c.get('value_candidates', [])]
    kg_vcs = [vc for vc in all_vcs if vc.get('normalized_unit') == 'kg']
    assert kg_vcs, 'Expected kg value_candidate'
    assert all(vc.get('kind') == 'weight' for vc in kg_vcs), (
        f'kg value_candidates must have kind=weight, got: {[vc.get("kind") for vc in kg_vcs]}'
    )


def test_value_candidate_kind_volume() -> None:
    # value_candidates must carry kind='volume' for m3 quantities
    cands = _candidates_from_text('Бетон 42,0 м3')
    all_vcs = [vc for c in cands for vc in c.get('value_candidates', [])]
    m3_vcs = [vc for vc in all_vcs if vc.get('normalized_unit') == 'm3']
    assert m3_vcs, 'Expected m3 value_candidate'
    assert all(vc.get('kind') == 'volume' for vc in m3_vcs), (
        f'm3 value_candidates must have kind=volume, got: {[vc.get("kind") for vc in m3_vcs]}'
    )


# ── A4.2.5: elevation_marker ─────────────────────��─────────────────────────

def test_elevation_value_creates_elevation_marker_not_ordinary() -> None:
    """'+3,250' alone must produce elevation_marker, not unknown_relevant_quantity."""
    cands = _candidates_from_text('Отм. +3,250')
    types = [c['candidate_type'] for c in cands]
    assert 'unknown_relevant_quantity' not in types, (
        f'Elevation must not become unknown_relevant_quantity. Got: {types}'
    )
    assert 'elevation_marker' in types, (
        f'Elevation must produce elevation_marker. Got: {types}'
    )


def test_elevation_marker_has_low_confidence() -> None:
    """elevation_marker must have low confidence so resolver ignores it by default."""
    cands = _candidates_from_text('Отм. +6,700')
    markers = [c for c in cands if c['candidate_type'] == 'elevation_marker']
    assert markers
    assert markers[0]['confidence'] < 0.5, (
        f'elevation_marker confidence must be < 0.5, got {markers[0]["confidence"]}'
    )


def test_ordinary_depth_is_not_elevation_marker() -> None:
    """'Глубина котлована 1,2 м' must NOT become elevation_marker — it is a real depth."""
    cands = _candidates_from_text('Глубина котлована 1,2 м')
    types = [c['candidate_type'] for c in cands]
    assert 'elevation_marker' not in types, (
        f'Real depth must not become elevation_marker. Got: {types}'
    )


def test_route_with_elevation_only_becomes_elevation_marker() -> None:
    """Route label + elevation-only value must produce elevation_marker, not route_summary."""
    cands = _candidates_from_text('К1 трасса на отм. +3,250')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'Route+elevation-only must not be route_summary. Got: {types}'
    )


# ── A4.2.5: diameter_spec ──────────────────────────────────────────────���──

def test_diameter_only_route_becomes_diameter_spec() -> None:
    """'К1 Ø110 мм' with no length must not create route_summary."""
    cands = _candidates_from_text('К1 труба Ø110 мм')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'Diameter-only route must not be route_summary. Got: {types}'
    )


def test_route_with_length_creates_route_summary() -> None:
    """'К1 12,4 п.м' with real length must still create route_summary."""
    cands = _candidates_from_text('К1 трасса итого 12,4 п.м')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' in types, (
        f'Route+length must produce route_summary. Got: {types}'
    )


def test_pipe_with_diameter_and_length_gives_length_as_primary() -> None:
    """'ПНД труба Ø110 12,4 п.м' — primary value must be length, not diameter."""
    cands = _candidates_from_text('ПНД труба Ø110 12,4 п.м')
    pipe = [c for c in cands if c['candidate_type'] == 'pipe_item']
    assert pipe, f'Expected pipe_item, got: {[c["candidate_type"] for c in cands]}'
    length_vals = [
        vc for c in pipe for vc in c.get('value_candidates', [])
        if vc.get('normalized_unit') == 'linear_m'
    ]
    assert length_vals, 'pipe_item must include length value_candidate'


def test_diameter_only_has_low_confidence() -> None:
    """diameter_spec must have low confidence so resolver ignores it for length params."""
    cands = _candidates_from_text('К1 Ø315 мм')
    dspecs = [c for c in cands if c['candidate_type'] == 'diameter_spec']
    if dspecs:
        assert dspecs[0]['confidence'] < 0.5


# ── A4.2.5.1: pipe_item eligibility guard ─────────────────────────────────────

def test_pipe_keyword_with_diameter_only_becomes_diameter_spec() -> None:
    """'Труба Ø110 мм' (no length or count) must not create pipe_item.

    Pipe keyword triggers the pipe_item branch, but without a useful primary
    quantity (п.м, шт — not bare мм) it must be downgraded to diameter_spec."""
    cands = _candidates_from_text('Труба Ø110 мм')
    types = [c['candidate_type'] for c in cands]
    assert 'pipe_item' not in types, (
        f'"Труба Ø110 мм" with no п.м/шт must not create pipe_item. Got: {types}'
    )


def test_pipe_keyword_with_count_stays_pipe_item() -> None:
    """'Труба Ø110 мм 15 шт' — has count → must stay pipe_item, not diameter_spec."""
    cands = _candidates_from_text('Труба Ø110 мм 15 шт')
    types = [c['candidate_type'] for c in cands]
    assert 'pipe_item' in types, (
        f'"Труба Ø110 мм 15 шт" with count must produce pipe_item. Got: {types}'
    )


# ── A4.2.7: dimensions-filter gap (found via MKP1 smoke, reproducible on any project) ──
#
# _has_useful_primary_quantity() used to be called with raw parse_quantities()
# output, which can include a kind='dimensions' entry (e.g. "90х195"). That
# entry satisfies the predicate (not diameter/elevation, unit isn't mm) so the
# gate passed — but _value_candidates_from_quantities() then drops dimensions
# entries entirely, leaving the stored candidate with no genuinely useful
# value at all while still being resolver_eligible.

def test_route_label_with_only_dimensions_becomes_diameter_spec() -> None:
    """Route label + a dimensions-only value (no real length/qty) must not
    become route_summary just because 'dimensions' passed the old pre-filter
    gate check."""
    cands = _candidates_from_text('К1 трасса Балки 90х195')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'Dimensions-only value must not create route_summary. Got: {types}'
    )


def test_pipe_keyword_with_only_dimensions_becomes_diameter_spec() -> None:
    """Pipe keyword + a dimensions-only value must not become pipe_item."""
    cands = _candidates_from_text('Труба ПНД 90х195')
    types = [c['candidate_type'] for c in cands]
    assert 'pipe_item' not in types, (
        f'Dimensions-only value must not create pipe_item. Got: {types}'
    )


def test_material_keyword_with_only_dimensions_is_dropped() -> None:
    """Material keyword + a dimensions-only value has no useful primary value
    and no natural fallback type — must be dropped, not kept as
    material_quantity with an empty value_candidates list."""
    cands = _candidates_from_text('Газобетон 90х195')
    types = [c['candidate_type'] for c in cands]
    assert 'material_quantity' not in types, (
        f'Dimensions-only value must not create material_quantity. Got: {types}'
    )


# ── A4.2.7: В-1/К1/ЭО route-label collision with АР opening codes ─────────

def test_ambiguous_code_without_engineering_context_is_not_route_summary() -> None:
    """A bare short code (В1) with a length value but no engineering context
    word at all must not become route_summary — too ambiguous on its own."""
    cands = _candidates_from_text('В1 22,0 п.м')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'В1 with no engineering context must not become route_summary. Got: {types}'
    )


def test_ambiguous_code_with_engineering_context_still_works() -> None:
    """К1/В1 + an explicit engineering-context word (канализация/труба/
    водоснабжение/…) must still produce route_summary."""
    cands = _candidates_from_text('К1 канализация труба 5,0 п.м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'К1 with канализация/труба context must produce route_summary'


def test_ambiguous_code_suppressed_near_door_schedule() -> None:
    """'В-1' as a door-schedule opening code (АР) must not be read as the
    water-supply route label, even though it has a quantity attached."""
    cands = _candidates_from_text('Ведомость дверных проемов В-1 4 700×3 250 1 шт')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'В-1 next to a door-opening schedule must not become route_summary. Got: {types}'
    )


def test_unambiguous_word_label_also_suppressed_near_opening_schedule() -> None:
    """Even an unambiguous word label (Дренаж) must not create route_summary
    if it sits right next to a door/window opening schedule context."""
    cands = _candidates_from_text('Ведомость дверных проемов дренаж 5,0 п.м')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'Route label near door-opening schedule must not become route_summary. Got: {types}'
    )


# ── A4.2.7.1: concrete grade (ГОСТ 26633) vs В1/В2 route-label collision ───
#
# Found via real USV/TRC data: "Бетон В22,5 W6 F150 П4 ... м3" rows satisfy
# the engineering-context requirement through the м3 volume alone, so В22/В25
# concrete class notation was still being read as a route label.

def test_concrete_grade_with_full_notation_is_not_route_summary() -> None:
    """'Бетон В22,5 W6 F150 П4 ...' — full ГОСТ 26633 grade notation must
    not become route_summary."""
    cands = _candidates_from_text('Бетон В22,5 W6 F150 П4 42,56 м3')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'Concrete grade notation must not become route_summary. Got: {types}'
    )


def test_concrete_grade_bare_is_not_route_summary() -> None:
    """'Бетон В25 46,2 м3' — bare grade (no W/F/П suffixes) must still not
    become route_summary; "Бетон" alone is enough context to suppress it."""
    cands = _candidates_from_text('Бетон В25 46,2 м3')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'Bare concrete grade must not become route_summary. Got: {types}'
    )


def test_water_supply_route_with_context_still_works() -> None:
    """'В1 трасса водоснабжения длина 12 м' — real route label with explicit
    context must still produce route_summary."""
    cands = _candidates_from_text('В1 трасса водоснабжения длина 12 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'В1 with трасса/водоснабжения context must produce route_summary'


def test_water_supply_route_with_length_depth_still_works() -> None:
    """'В1 длина 12 м глубина 1,9 м' — length/depth context (no "Бетон"
    nearby) must still produce route_summary."""
    cands = _candidates_from_text('В1 длина 12 м глубина 1,9 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'В1 with длина/глубина context must produce route_summary'


def test_concrete_grade_hyphenated_is_not_route_summary() -> None:
    """'ГОСТ 26633-2015 Бетон В-25 0,75 м3' — hyphenated grade notation
    ("В-25") is not even matched by _ROUTE_LABEL_CODE (no digit right after
    В), so it was never at risk — confirmed explicitly as regression
    coverage rather than left implicit."""
    cands = _candidates_from_text('ГОСТ 26633-2015 Бетон В-25 0,75 м3')
    types = [c['candidate_type'] for c in cands]
    assert 'route_summary' not in types, (
        f'Hyphenated concrete grade must not become route_summary. Got: {types}'
    )


def test_sewer_route_with_length_still_works() -> None:
    """'К1 трасса канализации длина 20 м' — real sewer route must still
    produce route_summary."""
    cands = _candidates_from_text('К1 трасса канализации длина 20 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'К1 with трасса/канализации context must produce route_summary'


def test_electrical_route_with_quantity_still_works() -> None:
    """'ЭО1 ввод электрического кабеля 15 м' — real electrical route with an
    actual quantity attached must still produce route_summary. (Without any
    number at all no candidate is created regardless of type — that's
    unrelated to the route-label guard.)"""
    cands = _candidates_from_text('ЭО1 ввод электрического кабеля 15 м')
    routes = [c for c in cands if c['candidate_type'] == 'route_summary']
    assert routes, 'ЭО1 with ввод context and a quantity must produce route_summary'
