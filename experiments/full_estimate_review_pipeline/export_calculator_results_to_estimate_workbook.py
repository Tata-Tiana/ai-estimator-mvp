from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOGO_PATH = REPO_ROOT / "experiments" / "earthworks_review_to_calculator" / "assets" / "brick_house_logo.png"

TITLE_TEXT = "СМЕТНЫЙ РАСЧЕТ НА СТРОИТЕЛЬСТВО ДОМА"
GROUP_HEADER_ROW = 9
SUBHEADER_ROW = 10
FIRST_SECTION_ROW = 11

SECTION_ORDER: list[tuple[str, str]] = [
    ("earthworks", "ЗЕМЛЯНЫЕ РАБОТЫ"),
    ("foundation_slab", "УСТРОЙСТВО ФУНДАМЕНТНОЙ ПЛИТЫ"),
    ("waterproofing", "ГИДРОИЗОЛЯЦИЯ, УТЕПЛЕНИЕ БОРТОВ ПЛИТ"),
    ("load_bearing_walls_lintels_p6", "ВНЕШНИЕ И ВНУТРЕННИЕ НЕСУЩИЕ СТЕНЫ, ПЕРЕМЫЧКИ НАД ПРОЕМАМИ"),
    # floor_slab_1/floor_slab_2 removed here (P3, FLOOR_SLAB_UNIFICATION_PLAN.md) - they used to
    # be two fixed entries in this exact spot. Now a dynamic number of blocks (as many as there
    # are real pours - 2 for every project today, since no real extraction has zone_context yet)
    # gets spliced in right after load_bearing_walls_lintels - see FLOOR_SLABS_INSERT_AFTER and
    # _all_section_blocks() below. "Honestly reflects reality: however many plates exist, that
    # many blocks land in the smeta" - the user's own framing when choosing this design.
    ("flat_roof", "ПЛОСКАЯ КРОВЛЯ"),
    ("schiedel_vent_channels", "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ"),
]

FLOOR_SLABS_INSERT_AFTER = "load_bearing_walls_lintels_p6"
FLOOR_SLABS_RESULT_FILENAME = "floor_slabs_result.json"

CALC_COLS = {
    "quantity": "J",
    "material_unit_price": "K",
    "material_total": "L",
    "work_unit_price": "M",
    "work_total": "N",
    "row_total": "O",
}
WHITE_ZONE_MIRROR = {
    "D": "J",
    "E": "K",
    "F": "L",
    "G": "M",
    "H": "N",
    "I": "O",
}

_GREY = PatternFill("solid", fgColor="FFB7B7B7")
_WHITE = PatternFill("solid", fgColor="FFFFFFFF")
_SECTION = PatternFill("solid", fgColor="FFEFEFEF")
_TOTAL = PatternFill("solid", fgColor="FFD9EAF7")
_THIN = Side(style="thin", color="303030")
_BLUE = Side(style="thick", color="1D4ED8")
_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)
_SPLIT = Border(left=_BLUE, right=_THIN, top=_THIN, bottom=_THIN)


def _num(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(_text(item) for item in value if item is not None)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _line_value(line: dict[str, Any], key: str) -> Any:
    if key in line and line.get(key) not in (None, ""):
        return line.get(key)
    internal_cost = line.get("internal_cost") or {}
    if isinstance(internal_cost, dict):
        return internal_cost.get(key)
    return None


def _quantity(line: dict[str, Any]) -> float:
    for key in ("quantity_raw", "quantity", "quantity_display"):
        if line.get(key) not in (None, ""):
            return _num(line.get(key))
    return 0.0


def _cost_parts(line: dict[str, Any]) -> tuple[float, float, float, float, float, float]:
    quantity = _quantity(line)
    material_total = _num(_line_value(line, "material_total"))
    work_total = _num(_line_value(line, "work_total"))
    row_total = _num(_line_value(line, "line_total")) or material_total + work_total

    material_unit_price = _num(_line_value(line, "material_unit_price"))
    work_unit_price = _num(_line_value(line, "work_unit_price"))

    # Some production calculators return percentage/fixed rows as totals, not as a
    # meaningful unit price. The Excel estimate should still keep live row formulas,
    # so represent such rows as quantity * derived unit price.
    if quantity and material_total and not material_unit_price:
        raw_total = _num(_line_value(line, "material_total_raw"))
        material_unit_price = (raw_total or material_total) / quantity
    if quantity and work_total and not work_unit_price:
        raw_total = _num(_line_value(line, "work_total_raw"))
        work_unit_price = (raw_total or work_total) / quantity

    return quantity, material_unit_price, material_total, work_unit_price, work_total, row_total


def _load_lines(results_dir: Path, section_code: str) -> list[dict[str, Any]]:
    path = results_dir / f"{section_code}_result.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    result = data.get("result", data)
    return list(result.get("estimate_lines") or result.get("lines") or [])


def _load_calculation_blocks(results_dir: Path, section_code: str) -> dict[str, Any]:
    path = results_dir / f"{section_code}_result.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    result = data.get("result", data)
    return result.get("calculation_blocks") or {}


def _load_floor_slabs_blocks(results_dir: Path) -> list[tuple[str, list[dict[str, Any]]]]:
    """P3: reads floor_slabs_result.json (produced by build_floor_slabs_result_json.py, see that
    script's own docstring) - {"pours": [{"title", "estimate_lines"}, ...]}. Raises on a missing
    file, same as _load_lines() does for every other section's JSON - a smeta silently missing
    both floor-slab sections because the file was never generated is worse than a loud crash."""
    path = results_dir / FLOOR_SLABS_RESULT_FILENAME
    data = json.loads(path.read_text(encoding="utf-8"))
    return [(pour["title"], list(pour.get("estimate_lines") or [])) for pour in data.get("pours") or []]


_REBAR_PRICE_CODE_RE = re.compile(r"^rebar_(?P<steel_class>[a-z0-9]+)_d(?P<diameter>\d+)_m$")


def _rebar_pool_label(price_code: str) -> str:
    match = _REBAR_PRICE_CODE_RE.match(price_code)
    if not match:
        return "Арматура"
    # Same "<class> ф<diameter>" convention as rebar_diameter_breakdown() in
    # populate_review_workbook_from_extraction.py (Этап 1, sheet 01's per-section/box summary) -
    # one shared label style for both places Elena sees a pooled rebar row.
    return f"{match.group('steel_class').upper()} ф{match.group('diameter')}"


def _rebar_zone_suffix(name: str) -> str:
    """Rebar line names carry their zone as a ": <zone>" suffix (P6 walls convention, e.g.
    "Арматура А500С Ø10 для кладки: Стены 1 этаж"). Sections with only one zone per line (single-
    pour sections like foundation_slab) never have this suffix, so they get "" - same pooling as
    before (fully collapsed by diameter, no zone split)."""
    if ": " in name:
        return name.rsplit(": ", 1)[-1]
    return ""


def _slugify_zone(zone: str) -> str:
    return "_".join(zone.lower().split())


def _rebar_diameter(price_code: str) -> int:
    match = _REBAR_PRICE_CODE_RE.match(price_code)
    return int(match.group("diameter")) if match else -1


def _sort_rebar_runs_by_diameter_desc(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Elena's real smetas always list rebar (within one construction stage) from the largest
    diameter down to the smallest - confirmed across foundation_slab/walls/lintels on multiple
    real projects, regardless of what order the spec-table positions happened to appear in the
    PDF. Sorts every maximal run of consecutive pooled rebar rows by diameter descending; runs
    stay separate wherever a non-rebar line already splits them (e.g. P6 walls' masonry-chasing
    rebar vs lintel rebar are different construction stages, kept apart by the lines between
    them - this only reorders diameters within a stage, never merges stages)."""
    result: list[dict[str, Any]] = []
    run: list[dict[str, Any]] = []

    def flush() -> None:
        if run:
            run.sort(key=lambda line: -_rebar_diameter(line.get("price_code") or ""))
            result.extend(run)
            run.clear()

    for line in lines:
        price_code = line.get("price_code") or ""
        if price_code.startswith("rebar_"):
            run.append(line)
        else:
            flush()
            result.append(line)
    flush()
    return result


def _pool_rebar_lines(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Этап 2 (2026-08-12, Elena's request): the smeta gets only one row per (steel_class,
    diameter) - price_code already uniquely identifies that combo (rebar_<class>_d<diameter>_m) -
    not the position-level "zoo" (хомуты/лягушки/выпуски/etc) the calculators still produce for
    traceability. Elena doesn't show the position breakdown in her own real smetas either, and
    isn't the one who can change rebar quantities without the structural engineer's sign-off
    anyway - only these pooled summary rows are hers to round up or add a reserve to if she wants.
    Every non-rebar line (price_code not starting with "rebar_") passes through unchanged, in its
    original position; pooled rebar rows appear where the first line of that diameter/class did.

    Fixed 2026-08-14: pooling key is now (price_code, zone) instead of price_code alone. Sections
    with more than one zone inside them (currently only load_bearing_walls_lintels_p6 - 1-й/2-й
    этаж/парапет all live in one section, unlike every other section which is single-zone) were
    getting their rebar collapsed across zones, contradicting Elena's real smetas which always
    keep rebar-by-diameter separate per floor (confirmed against all 3 real projects, see
    P6_WALLS_LINTELS_DATA_CONTRACT.md). Single-zone sections are unaffected - their lines have no
    ": zone" suffix, so zone_key is always "" and pooling stays exactly as before."""
    result: list[dict[str, Any]] = []
    index_by_key: dict[tuple[str, str], int] = {}
    for line in lines:
        price_code = line.get("price_code") or ""
        if not price_code.startswith("rebar_"):
            result.append(line)
            continue
        zone = _rebar_zone_suffix(line.get("name") or "")
        key = (price_code, zone)
        if key in index_by_key:
            pooled = result[index_by_key[key]]
        else:
            label = _rebar_pool_label(price_code)
            code = f"{price_code}_pooled"
            if zone:
                label = f"{label}: {zone}"
                code = f"{code}_{_slugify_zone(zone)}"
            pooled = {
                "code": code,
                "name": label,
                "unit": line.get("unit") or "мп",
                "quantity": 0.0,
                "material_unit_price": _num(line.get("material_unit_price")),
                "material_total": 0.0,
                "work_unit_price": _num(line.get("work_unit_price")),
                "work_total": 0.0,
                "line_total": 0.0,
                "price_code": price_code,
            }
            index_by_key[key] = len(result)
            result.append(pooled)
        pooled["quantity"] += _quantity(line)
        pooled["material_total"] += _num(_line_value(line, "material_total"))
        pooled["work_total"] += _num(_line_value(line, "work_total"))
        pooled["line_total"] += _num(_line_value(line, "line_total"))
    return _sort_rebar_runs_by_diameter_desc(result)


_ZONE_SUBHEADER_MARKER = "__zone_subheader__"
_MASONRY_WORK_LABEL = "Кладка внешних, внутренних стен из газобетонных блоков"

# Mirrors load_bearing_walls_lintels_p6_calculator.py's own _delivery_batch_id()/_crane_batch_id()
# exactly (must stay in sync - these decide which zones' block deliveries/crane lifts get pooled
# into one shared line). Needed here only to know which zone a shared batch's line should visually
# sit under once _regroup_p6_lines_by_zone() below re-attaches it - the calculator itself has no
# concept of "which zone owns the printed row", it just emits pooled batches after all zones.
_UPPER_GROUP_ZONE_KINDS = {"floor_2", "second_light", "parapet", "vent_chimney_cladding"}


def _delivery_batch_id_for_zone(zone_id: str, zone_kind: str | None) -> str:
    return "upper_parapet_vent" if zone_kind in _UPPER_GROUP_ZONE_KINDS else zone_id


def _crane_batch_id_for_zone(zone_id: str, zone_kind: str | None) -> str:
    return "parapet" if zone_kind == "parapet" else _delivery_batch_id_for_zone(zone_id, zone_kind)


_BLOCKS_LOGISTICS_CODE_RE = re.compile(r"^(?P<batch_id>.+)_blocks_(?P<kind>delivery|unloading_manipulator|crane_moving)$")

# Elena's real smetas (checked ТРЦ 1-й/2-й этаж/парапет, all 3 reproduce the same order) always
# print one zone in the same physical-construction order: waterproofing prep, then the masonry
# stage complete with its own rebar/delivery/crane, THEN the lintel stage (formwork, its rebar,
# concreting, concrete logistics) as a separate block, THEN insulation last. Ranked purely off each
# line's own `code` suffix - the calculator names these identically regardless of project, so this
# generalizes to any project through this same calculator, not just today's real one. Block
# material lines all share one rank (20) and get a secondary density-based sort below (D400 before
# D500, matching both real floors checked) since a zone can have more than one.
#
# Order in this list matters, not just the rank number: the first pattern that matches wins (see
# _p6_line_role_rank() below). Block-material lines used to be matched here too via a generic
# "_block_<anything-without-an-underscore>$" pattern - removed 2026-08-26 after real ЮСВ/ТРЦ smetas
# showed газоблок D400/D500 rows landing at the very END of every zone instead of right after
# Кладка. Root cause: real block item_ids always contain their own underscores (f1_400, f1_250,
# main_250_1, parapet_400, vent_150...), so "..._block_f1_400" never matched "[^_]+$" - the pattern
# silently never fired for any real project, and every block-material line fell through to the
# unrecognized-code default (999, last place). Block material is now matched by `price_code`
# instead (_p6_line_role_rank() below, checked before this list) - price_code is a small fixed set
# (gas_block_d400_m3/gas_block_d500_m3/gas_block_d500_150_m3), not a free-form code suffix, so it
# can't break the same way if a project ever uses an item_id shaped differently again.
_P6_LINE_ROLE_RANK: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"_cutoff_waterproofing_under_first_row_blocks$"), 0),
    (re.compile(r"_masonry_work$"), 10),
    (re.compile(r"_gas_block_cladding_work$"), 10),
    (re.compile(r"_u_block_lintel_cutting$"), 30),
    (re.compile(r"_block_adhesive$"), 40),
    (re.compile(r"_sand_concrete_m300_first_row$"), 50),
    (re.compile(r"_chasing_for_reinforcement$"), 60),
    # masonry/parapet-chasing rebar -> 70 (matched via code below, price_code alone can't tell
    # "для кладки" apart from "для перемычек" - both share the same rebar_<class>_d<n>_m code)
    (re.compile(r"_blocks_delivery$"), 80),
    (re.compile(r"_blocks_unloading_manipulator$"), 81),
    (re.compile(r"_blocks_crane_moving$"), 82),
    (re.compile(r"_lintel_formwork_installation$"), 100),
    (re.compile(r"_lintel_formwork_plywood_material$"), 110),
    (re.compile(r"_lintel_formwork_timber_material$"), 120),
    (re.compile(r"_lintel_rebar_frame_assembly$"), 130),
    # lintels-purpose rebar -> 140
    (re.compile(r"_u_block_lintel_concreting_work$"), 150),
    (re.compile(r"_monolithic_lintel_concreting_work$"), 151),
    (re.compile(r"_lintel_concrete_b22_5_m300_material$"), 160),
    (re.compile(r"_lintel_concrete_delivery$"), 170),
    (re.compile(r"_manual_concrete_lifting$"), 180),
    (re.compile(r"_lintel_formwork_dismantling$"), 185),
    (re.compile(r"_lintel_edge_insulation_work$"), 190),
    (re.compile(r"_lintel_edge_insulation_eps_material$"), 200),
    (re.compile(r"_lintel_edge_insulation_glue_foam$"), 210),
]
_MASONRY_CHASING_REBAR_RE = re.compile(r"_(masonry_chasing|parapet_chasing)_rebar_")
_LINTEL_REBAR_RE = re.compile(r"_lintels_rebar_")
_BLOCK_DENSITY_ORDER = {"D400": 0, "D500": 1}
# The 3 fixed price_codes _block_price_code() in the calculator assigns to gas-block material
# lines - matched directly instead of parsing `code` (see _P6_LINE_ROLE_RANK's comment above for
# why the old code-suffix regex silently never matched any real project's block-material lines).
_BLOCK_MATERIAL_PRICE_CODES = {"gas_block_d400_m3", "gas_block_d500_m3", "gas_block_d500_150_m3"}


def _p6_line_role_rank(entry: dict[str, Any]) -> tuple[int, int]:
    code = entry.get("code") or ""
    price_code = entry.get("price_code") or ""
    if price_code.startswith("rebar_"):
        if _MASONRY_CHASING_REBAR_RE.search(code):
            return (70, 0)
        if _LINTEL_REBAR_RE.search(code):
            return (140, 0)
        return (70, 0)  # unknown purpose - default to the masonry-stage slot, never dropped
    if price_code in _BLOCK_MATERIAL_PRICE_CODES:
        name = entry.get("name") or ""
        density_match = re.search(r"D-?(\d00)", name)
        density_rank = _BLOCK_DENSITY_ORDER.get(f"D{density_match.group(1)}", 2) if density_match else 2
        return (20, density_rank)
    for pattern, rank in _P6_LINE_ROLE_RANK:
        if pattern.search(code):
            return (rank, 0)
    return (999, 0)  # anything unrecognized keeps its place at the end of the zone, never dropped


def _regroup_p6_lines_by_zone(
    lines: list[dict[str, Any]], calculation_blocks: dict[str, Any]
) -> list[dict[str, Any]]:
    """Elena's real smetas print each zone's rebar and its delivery/unloading/crane rows directly
    inside that zone's own block, right after its other lines - never collected separately.
    load_bearing_walls_lintels_p6_calculator.py can't do this itself: rebar is pooled across the
    whole wall_zones list in one pass (_pool_rebar_by_zone_purpose), and a delivery/crane batch can
    span several zones (floor_2+parapet+vent_chimney_cladding share one truck) - both only make
    sense to compute after every zone has been processed, so both naturally land at the end of the
    line list, correctly labelled per zone in their own `name` but visually glued together in one
    lump instead of split across zones. This walks the already-emitted line list once and moves
    each rebar/logistics line back to sit right after the zone it belongs to - a presentation fix
    only, changes row order, never a quantity or price."""
    zones_meta = calculation_blocks.get("zones") or {}
    zone_order = list(zones_meta.keys())
    if not zone_order:
        return lines
    zone_kind_by_id = {zid: (meta or {}).get("zone_kind") for zid, meta in zones_meta.items()}
    display_name_by_zone = {zid: (meta or {}).get("display_name") or zid for zid, meta in zones_meta.items()}
    zone_by_display_name = {name: zid for zid, name in display_name_by_zone.items()}

    delivery_batch_target: dict[str, str] = {}
    crane_batch_target: dict[str, str] = {}
    for zid in zone_order:
        kind = zone_kind_by_id.get(zid)
        delivery_batch_target.setdefault(_delivery_batch_id_for_zone(zid, kind), zid)
        crane_batch_target.setdefault(_crane_batch_id_for_zone(zid, kind), zid)

    # Longest-prefix-first so no zone_id can shadow a longer sibling that happens to start with
    # the same characters (not a real risk with today's zone_id vocabulary, but cheap to guard).
    zone_ids_by_prefix_length = sorted(zone_order, key=len, reverse=True)

    pre_zone: list[dict[str, Any]] = []
    zone_base: dict[str, list[dict[str, Any]]] = {zid: [] for zid in zone_order}
    zone_rebar: dict[str, list[dict[str, Any]]] = {zid: [] for zid in zone_order}
    zone_logistics: dict[str, list[dict[str, Any]]] = {zid: [] for zid in zone_order}
    tail: list[dict[str, Any]] = []

    current_zone: str | None = None
    for entry in lines:
        code = entry.get("code") or ""
        name = entry.get("name") or ""
        price_code = entry.get("price_code") or ""

        # Zone-transition detection can't rely on "_masonry_work" alone - a zone without regular
        # masonry (e.g. vent_chimney_cladding, see _zone_has_regular_masonry() in the calculator)
        # never emits that code at all, so its own lines would otherwise get glued onto whichever
        # zone happened to run right before it. Matches any line whose code starts with a real
        # zone_id, not just the masonry-work one.
        for zid in zone_ids_by_prefix_length:
            if code == f"{zid}_masonry_work" or code.startswith(f"{zid}_"):
                current_zone = zid
                break

        if code.endswith("_masonry_work"):
            zone_base[current_zone].append(entry)
            continue

        if current_zone is None:
            pre_zone.append(entry)
            continue

        zone_suffix = _rebar_zone_suffix(name)
        is_rebar_like = price_code.startswith("rebar_") or code.endswith("_lintel_rebar_frame_assembly")
        if is_rebar_like and zone_suffix in zone_by_display_name:
            zone_rebar[zone_by_display_name[zone_suffix]].append(entry)
            continue

        match = _BLOCKS_LOGISTICS_CODE_RE.match(code)
        if match:
            batch_id = match.group("batch_id")
            target = (
                crane_batch_target.get(batch_id)
                if match.group("kind") == "crane_moving"
                else delivery_batch_target.get(batch_id)
            )
            if target is not None:
                zone_logistics[target].append(entry)
                continue

        # Known section-tail codes (consumables/waste/tech supervision/markup) - never zone-owned,
        # regardless of how far current_zone tracking has drifted by this point in the line list.
        if code in {
            "walls_consumables_tool_amortization",
            "construction_waste_removal",
            "walls_technical_supervision",
            "procurement_warehouse_costs",
            "overhead_general_business_costs",
            "estimated_profit",
        }:
            tail.append(entry)
            continue

        zone_base[current_zone].append(entry)

    # A zone with no masonry_work line of its own (e.g. vent_chimney_cladding -
    # _zone_has_regular_masonry() in the calculator) never gets a subheader (see below) - and
    # Elena's real smetas never print it as its own separate block either, they fold its lines
    # into whichever real zone came right before it (checked on the real ТРЦ: обкладка
    # дымохода/вентканалов sits interleaved inside "Парапет", not as its own section). Redistribute
    # BEFORE sorting, not after, so the merged-in lines interleave by role instead of just landing
    # at the end of the target zone's own already-sorted block. Falls back to keeping a no-masonry
    # zone as its own (subheader-less) block only if it's first in zone_order with nothing real
    # to merge into yet - an edge case never seen on any real project so far.
    has_own_masonry_work = {
        zid: any((e.get("code") or "").endswith("_masonry_work") for e in zone_base[zid])
        for zid in zone_order
    }
    target_zone = {}
    last_real_zone: str | None = None
    for zid in zone_order:
        if has_own_masonry_work[zid]:
            last_real_zone = zid
        target_zone[zid] = last_real_zone if last_real_zone is not None else zid
    for zid in zone_order:
        target = target_zone[zid]
        if target == zid:
            continue
        zone_base[target].extend(zone_base.pop(zid))
        zone_rebar[target].extend(zone_rebar.pop(zid))
        zone_logistics[target].extend(zone_logistics.pop(zid))

    result = list(pre_zone)
    for zid in [z for z in zone_order if target_zone[z] == z]:
        combined = zone_base[zid] + zone_rebar[zid] + zone_logistics[zid]
        # Stable sort - only _p6_line_role_rank() decides relative order now (see its own comment
        # for the exact role sequence, verified against 3 real zones); ties keep whatever order the
        # calculator itself emitted them in, which is already a sane fallback for any role this
        # ranking doesn't recognize.
        combined.sort(key=_p6_line_role_rank)
        if not combined:
            continue
        # Subheader insertion has to happen here, after sorting, not in a separate later pass keyed
        # on "_masonry_work" position (used to be safe when that line was always first - waterproofing
        # now legitimately sorts ahead of it within the same zone, which would otherwise land the
        # subheader in the middle of its own zone's block). Only zones with a real masonry_work line
        # get a subheader at all - matches _zone_has_regular_masonry() in the calculator itself
        # (vent_chimney_cladding has none, and correctly stays glued under whichever zone precedes it,
        # exactly like Elena's real smetas never give it its own subheader either).
        has_masonry_work = any((e.get("code") or "").endswith("_masonry_work") for e in combined)
        if has_masonry_work:
            result.append({_ZONE_SUBHEADER_MARKER: True, "name": display_name_by_zone[zid]})
            for entry in combined:
                if (entry.get("code") or "").endswith("_masonry_work"):
                    entry = {**entry, "name": _MASONRY_WORK_LABEL}
                result.append(entry)
        else:
            result.extend(combined)
    result.extend(tail)
    return result


def _all_section_blocks(results_dir: Path) -> list[tuple[str, list[dict[str, Any]]]]:
    """Full ordered list of (title, lines) blocks to render - SECTION_ORDER's 6 fixed sections
    plus the dynamic floor-slabs block spliced in right after FLOOR_SLABS_INSERT_AFTER, in the
    exact spot floor_slab_1/floor_slab_2 used to occupy as two fixed entries."""
    blocks: list[tuple[str, list[dict[str, Any]]]] = []
    for section_code, section_title in SECTION_ORDER:
        if section_code == "load_bearing_walls_lintels_p6":
            # Regroup BEFORE pooling, not after: _pool_rebar_lines() replaces each rebar line's
            # `code` with a synthetic "<price_code>_pooled_<zone>" one, which destroys the
            # "..._masonry_chasing_rebar_..." / "..._lintels_rebar_..." substring
            # _p6_line_role_rank() needs to tell masonry rebar (stage 1) apart from lintel rebar
            # (stage 2) - price_code alone can't (same rebar_<class>_d<n>_m regardless of purpose).
            # The raw calculator lines still carry that substring; pooling only needs to happen once
            # they're already in final order, since it accumulates into the first-seen position for
            # each (price_code, zone) key either way.
            calculation_blocks = _load_calculation_blocks(results_dir, section_code)
            lines = _regroup_p6_lines_by_zone(_load_lines(results_dir, section_code), calculation_blocks)
            lines = _pool_rebar_lines(lines)
        else:
            lines = _pool_rebar_lines(_load_lines(results_dir, section_code))
        blocks.append((section_title, lines))
        if section_code == FLOOR_SLABS_INSERT_AFTER:
            blocks.extend(
                (title, _pool_rebar_lines(lines))
                for title, lines in _load_floor_slabs_blocks(results_dir)
            )
    return blocks


def _extract_project_address(review_workbook: Path | None) -> str:
    if review_workbook is None or not review_workbook.exists():
        return "Адрес объекта: —"
    wb = load_workbook(review_workbook, data_only=True)
    if "01_Проверка проекта" not in wb.sheetnames:
        return "Адрес объекта: —"
    ws = wb["01_Проверка проекта"]
    for row in ws.iter_rows(values_only=True):
        label = _text(row[0] if row else "")
        if "адрес" not in label.lower():
            continue
        for value in row[1:4]:
            candidate = _text(value).strip()
            if candidate:
                return candidate
    return "Адрес объекта: —"


def _setup_top_header(ws: Any, logo_path: Path, address: str) -> None:
    for row in range(1, 9):
        for col in range(10, 23):
            ws.cell(row, col).fill = _GREY

    ws.merge_cells("A1:I4")
    if logo_path.exists():
        logo = OpenpyxlImage(str(logo_path))
        logo.width = 300
        logo.height = 50
        ws.add_image(logo, "C2")

    ws.merge_cells("A5:I5")
    ws["A5"].value = TITLE_TEXT
    ws["A5"].font = Font(size=12, bold=True)
    ws["A5"].alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells("A6:I6")
    ws["A6"].value = address
    ws["A6"].font = Font(size=10)
    ws["A6"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
    ws.row_dimensions[6].height = 24

    header_merges = [
        (GROUP_HEADER_ROW, 1, SUBHEADER_ROW, 1, "№"),
        (GROUP_HEADER_ROW, 2, SUBHEADER_ROW, 2, "Наименование работ"),
        (GROUP_HEADER_ROW, 3, SUBHEADER_ROW, 3, "Ед. изм."),
        (GROUP_HEADER_ROW, 4, SUBHEADER_ROW, 4, "Кол-во"),
        (GROUP_HEADER_ROW, 5, GROUP_HEADER_ROW, 6, "Стоимость материалов,\nмашин и механизмов, руб."),
        (GROUP_HEADER_ROW, 7, GROUP_HEADER_ROW, 8, "Стоимость работ, руб."),
        (GROUP_HEADER_ROW, 9, SUBHEADER_ROW, 9, "Итого, руб."),
        (GROUP_HEADER_ROW, 10, SUBHEADER_ROW, 10, "Кол-во"),
        (GROUP_HEADER_ROW, 11, GROUP_HEADER_ROW, 12, "Стоимость материалов,\nмашин и механизмов, руб."),
        (GROUP_HEADER_ROW, 13, GROUP_HEADER_ROW, 14, "Стоимость работ, руб."),
        (GROUP_HEADER_ROW, 15, SUBHEADER_ROW, 15, "Итого, руб."),
    ]
    for sr, sc, er, ec, value in header_merges:
        ws.merge_cells(start_row=sr, start_column=sc, end_row=er, end_column=ec)
        ws.cell(sr, sc).value = value

    for col, value in {
        5: "За ед",
        6: "Итого",
        7: "За ед",
        8: "Итого",
        11: "За ед",
        12: "Итого",
        13: "За ед",
        14: "Итого",
    }.items():
        ws.cell(SUBHEADER_ROW, col).value = value

    for row in (GROUP_HEADER_ROW, SUBHEADER_ROW):
        for col in range(1, 16):
            cell = ws.cell(row, col)
            cell.fill = _GREY if col >= 10 else _WHITE
            cell.border = _SPLIT if col == 10 else _BORDER
            cell.font = Font(size=10, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.row_dimensions[GROUP_HEADER_ROW].height = 46
    ws.row_dimensions[SUBHEADER_ROW].height = 22


def _setup_dimensions(ws: Any) -> None:
    widths = {
        1: 6,
        2: 58,
        3: 10,
        4: 12,
        5: 16,
        6: 16,
        7: 14,
        8: 14,
        9: 14,
        10: 12,
        11: 16,
        12: 16,
        13: 14,
        14: 14,
        15: 14,
    }
    for col_num, width in widths.items():
        ws.column_dimensions[get_column_letter(col_num)].width = width
    for col_num in range(16, 23):
        ws.column_dimensions[get_column_letter(col_num)].width = 10
    ws.freeze_panes = "E11"


def _write_section_header(ws: Any, row_num: int, section_number: int, section_title: str) -> None:
    for col in range(1, 23):
        cell = ws.cell(row_num, col)
        cell.fill = _GREY if col >= 10 else _SECTION
        cell.border = _SPLIT if col == 10 else _BORDER
        cell.font = Font(size=10, bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row_num, 1).value = section_number
    ws.cell(row_num, 2).value = section_title
    ws.cell(row_num, 2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[row_num].height = 22


def _write_zone_subheader(ws: Any, row_num: int, zone_name: str) -> None:
    """Empty row with just a bold zone name (e.g. "1-ый этаж") in column B - no fill, no data in
    any other column. Font matches every other row's own font (size 10), just bold - 2026-08-16
    design change, was size 14 to stand out more."""
    cell = ws.cell(row_num, 2)
    cell.value = _text(zone_name)
    cell.font = Font(size=10, bold=True)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row_num].height = 20


def _write_data_row(ws: Any, row_num: int, line: dict[str, Any]) -> None:
    quantity, material_unit, _material_total, work_unit, _work_total, _row_total = _cost_parts(line)

    ws.cell(row_num, 2).value = _text(line.get("name"))
    ws.cell(row_num, 3).value = _text(line.get("unit"))

    for white_col, grey_col in WHITE_ZONE_MIRROR.items():
        cell = ws[f"{white_col}{row_num}"]
        cell.value = f"={grey_col}{row_num}"
        cell.fill = _WHITE
        cell.border = _BORDER
        cell.font = Font(size=10)
        cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
        cell.number_format = "0.00" if white_col == "D" else "0"

    values = {
        "J": quantity,
        "K": material_unit,
        "L": f"=ROUND(J{row_num}*K{row_num},0)",
        "M": work_unit,
        "N": f"=ROUND(J{row_num}*M{row_num},0)",
        "O": f"=L{row_num}+N{row_num}",
    }
    for col, value in values.items():
        cell = ws[f"{col}{row_num}"]
        cell.value = value
        cell.fill = _GREY
        cell.border = _SPLIT if col == "J" else _BORDER
        cell.font = Font(size=10)
        cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
        cell.number_format = "0.00" if col == "J" else "0"

    for col in range(1, 23):
        cell = ws.cell(row_num, col)
        if col in (1, 16, 17, 18, 19, 20, 21, 22):
            cell.fill = _GREY if col >= 16 else _WHITE
            cell.border = _BORDER
        if col in (2, 3):
            cell.fill = _WHITE
            cell.border = _BORDER
            cell.font = Font(size=10)
            cell.alignment = Alignment(horizontal="left" if col == 2 else "center", vertical="top", wrap_text=True)

    ws.row_dimensions[row_num].height = 18


def _write_section_total(ws: Any, row_num: int, first_data_row: int, last_data_row: int) -> None:
    totals = {
        2: "Итого по разделу:",
        6: f"=L{row_num}",
        8: f"=N{row_num}",
        9: f"=O{row_num}",
        12: f"=SUM(L{first_data_row}:L{last_data_row})",
        14: f"=SUM(N{first_data_row}:N{last_data_row})",
        15: f"=SUM(O{first_data_row}:O{last_data_row})",
    }
    for col in range(1, 23):
        cell = ws.cell(row_num, col)
        cell.value = totals.get(col, "")
        cell.fill = _GREY if col >= 10 else _TOTAL
        cell.border = _SPLIT if col == 10 else _BORDER
        cell.font = Font(size=10, bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.number_format = "0"
    ws.row_dimensions[row_num].height = 22


def _write_grand_total(ws: Any, row_num: int, section_total_rows: list[int]) -> None:
    material_refs = ",".join(f"L{row}" for row in section_total_rows)
    work_refs = ",".join(f"N{row}" for row in section_total_rows)
    total_refs = ",".join(f"O{row}" for row in section_total_rows)
    totals = {
        2: "ИТОГО ПО СМЕТЕ:",
        6: f"=L{row_num}",
        8: f"=N{row_num}",
        9: f"=O{row_num}",
        12: f"=SUM({material_refs})",
        14: f"=SUM({work_refs})",
        15: f"=SUM({total_refs})",
    }
    for col in range(1, 23):
        cell = ws.cell(row_num, col)
        cell.value = totals.get(col, "")
        cell.fill = _GREY if col >= 10 else _TOTAL
        cell.border = _SPLIT if col == 10 else _BORDER
        cell.font = Font(size=11, bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.number_format = "0"
    ws.row_dimensions[row_num].height = 24


def build_workbook(results_dir: Path, review_workbook: Path | None, logo_path: Path) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = dt.date.today().strftime("%d.%m.%Y")

    _setup_top_header(ws, logo_path=logo_path, address=_extract_project_address(review_workbook))
    _setup_dimensions(ws)

    row_num = FIRST_SECTION_ROW
    section_total_rows: list[int] = []
    for section_number, (section_title, lines) in enumerate(_all_section_blocks(results_dir), start=2):
        _write_section_header(ws, row_num, section_number, section_title)
        row_num += 1
        first_data_row = row_num
        for line in lines:
            if line.get(_ZONE_SUBHEADER_MARKER):
                _write_zone_subheader(ws, row_num, line.get("name") or "")
            else:
                _write_data_row(ws, row_num, line)
            row_num += 1
        last_data_row = row_num - 1
        if first_data_row <= last_data_row:
            ws.merge_cells(start_row=first_data_row, start_column=1, end_row=last_data_row, end_column=1)
            section_cell = ws.cell(first_data_row, 1)
            section_cell.value = section_title
            section_cell.font = Font(size=10, bold=True)
            section_cell.fill = _WHITE
            section_cell.alignment = Alignment(horizontal="center", vertical="center", text_rotation=90, wrap_text=True)
            section_cell.border = _BORDER
        _write_section_total(ws, row_num, first_data_row, last_data_row)
        section_total_rows.append(row_num)
        row_num += 1

    row_num += 1
    _write_grand_total(ws, row_num, section_total_rows)
    ws.auto_filter.ref = f"A{GROUP_HEADER_ROW}:O{row_num}"

    return wb


def main() -> int:
    parser = argparse.ArgumentParser(description="Export all calculator section results to an estimate-style workbook.")
    parser.add_argument("--results-dir", required=True, help="Directory with <section>_result.json files.")
    parser.add_argument("--review-workbook", default=None, help="Optional filled review workbook for project metadata.")
    parser.add_argument("--out", required=True, help="Output .xlsx path.")
    parser.add_argument("--logo-path", default=str(DEFAULT_LOGO_PATH), help="Path to Brick House logo.")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    review_workbook = Path(args.review_workbook) if args.review_workbook else None
    out_path = Path(args.out)
    logo_path = Path(args.logo_path)

    wb = build_workbook(results_dir=results_dir, review_workbook=review_workbook, logo_path=logo_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    print(out_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
