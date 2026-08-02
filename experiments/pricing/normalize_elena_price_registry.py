from __future__ import annotations

import argparse
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "output" / "Цены на материалы.xlsx"
DEFAULT_ARCHIVE_SOURCE = ROOT / "experiments" / "pricing" / "input" / "price_registry_elena_2026-07-28.xlsx"
DEFAULT_PREVIOUS_REGISTRY = ROOT / "output" / "price_registry_filled_v3.xlsx"
DEFAULT_OUTPUT = ROOT / "output" / "price_registry_filled_v4.xlsx"
DEFAULT_REPORT = ROOT / "experiments" / "pricing" / "output" / "price_registry_v4_mapping_report.md"

REGISTRY_HEADERS = [
    "Раздел",
    "Наименование",
    "Ед. изм.",
    "Минимальная комплектация",
    "Цена",
    "Дата обновления",
    "Комментарий",
    "price_code",
]


def clean_text(value: Any) -> str:
    return "" if value is None else str(value).replace("\xa0", " ").strip()


def normalize_text(value: Any) -> str:
    text = clean_text(value).lower()
    text = text.replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_unit(value: Any) -> str:
    unit = normalize_text(value)
    aliases = {
        "1п.м": "мп",
        "1п. м": "мп",
        "п.м": "мп",
        "п. м": "мп",
        "м/п": "мп",
        "м.п": "мп",
        "м": "мп",
        "м2": "м2",
        "м²": "м2",
        "м3": "м3",
        "м³": "м3",
        "шт.": "шт",
        "смен": "смена",
    }
    return aliases.get(unit, unit)


def row_key(name: Any, unit: Any) -> tuple[str, str]:
    return normalize_text(name), normalize_unit(unit)


MANUAL_WORK_PRICE_CODES: dict[tuple[str, str], str] = {
    row_key(
        'Экскаватор-погрузчик JCB (раскопка "корыта" под устройство дороги) /Контроль за механизированной разработкой грунта',
        "смена",
    ): "excavator_jcb_shift",
    row_key(
        "Разработка грунта вручную (в т.ч. Копка траншей под коммуникации)",
        "м3",
    ): "manual_excavation_m3",
    row_key(
        "Отсыпка дна котлована песком с трамбованием механизировано с применением виброплиты (коэф.упл. 1,3)",
        "м3",
    ): "sand_filling_work_m3",
    row_key(
        "Закладка технологических входов коммуникаций до границы дома. Канализация, водоснабжение (ориентировочно)",
        "мп",
    ): "communications_installation_m",
    row_key("Устройство и монтаж термовкладыша", "мп"): "thermal_insert_installation_work_m",
    row_key(
        "Бетонирование фундаментной плиты в опалубке бетоном марки В22,5 (М300)",
        "м3",
    ): "concrete_placing_work_m3",
    row_key(
        "Гидроизоляция торца фундаментной плиты битумной мастикой в 2 слоя",
        "м2",
    ): "bitumen_waterproofing_work_m2",
    row_key("Утепление торца плиты ЭППС 100мм", "м2"): "eps_wall_insulation_work_m2",
    row_key(
        "Устройство лесов, подмостей для кладки, демонтаж лесов после завершения работ",
        "компл",
    ): "scaffolding_setup_dismantling_work_set",
    row_key(
        "Бетонирование перемычек в U блоке бетоном марки В22,5 (М300)",
        "мп",
    ): "lintel_concreting_work_m",
    row_key(
        "Бетонирование монолитных перемычек бетоном марки В22,5 (М300)",
        "мп",
    ): "lintel_monolithic_concreting_work_m",
    row_key(
        "Бетонирование балки бетоном марки В22,5 (М300) (высотой до 250мм)",
        "мп",
    ): "beam_concrete_placing_work_m",
    row_key("Вывоз мусора с объекта", "маш"): "waste_removal_loading_work_truck",
    row_key("Кладка парапета из газобетонных блоков", "м3"): "gas_block_masonry_work_m3",
    row_key(
        "Обкладка дымохода и вентканалов толщ. 150мм из из газобетонных блоков",
        "м2",
    ): "gas_block_cladding_work_m2",
    row_key("Пароизоляция основания плёнкой ПВХ", "м2"): "roof_vapor_barrier_installation_work_m2",
    row_key(
        "Утепление кровельного покрытия ЭППС (1 слой -100мм, 2 слой -100мм (50мм), 3 слой - разуклонка)",
        "м2",
    ): "roof_eps_insulation_installation_work_m2",
    row_key("Укладка ПВХ Мембраны", "м2"): "roof_pvc_membrane_installation_work_m2",
    row_key("Монтаж примыкания кровли из ПВХ мембраны", "мп"): "roof_pvc_membrane_abutment_work_m",
    row_key("Монтаж примыкания к вентшахтам", "шт"): "roof_vent_shaft_abutment_installation_item",
    row_key("Установка воронки парапетной", "шт"): "roof_parapet_drain_item",
    row_key("Подъем материалов автокраном / разгрузка материала в ручную", "смена"): "roof_crane_lifting_shift",
    row_key("Кладка вентканалов Schiedel", "мп"): "schiedel_masonry_work_m",
    row_key("Доставка вентканалов/ разгрузка в ручную на объекте", "маш"): "schiedel_delivery_truck",
}

IGNORED_WORK_PRICE_ROWS: set[tuple[str, str]] = {
    row_key(
        "Бетонирование балки бетоном марки В22,5 (М300) (высотой более 250мм)",
        "м3",
    ),
}

OBSOLETE_PREVIOUS_PRICE_CODES = {
    "beam_concrete_placing_work_m3",
    "waste_removal_truck",
}

PRICE_CODE_NAME_OVERRIDES = {
    "edge_insulation_work_m": "Устройство утепления по наружной стороне торцов плиты, балок, перемычек",
}

DERIVED_PRICE_ROWS = [
    {
        "section": "Работы",
        "name": "Устройство утепления по наружной стороне торцов плиты, балок, перемычек",
        "unit": "мп",
        "min_quantity": 1,
        "price": 450,
        "price_code": "lintel_edge_insulation_work_m",
        "comment": "Добавлено по ответу Елены 2026-07-30: ставка такая же, как утепление балок и торца плиты.",
    },
    {
        "section": "Работы",
        "name": "Установка аэратора кровельного PVC, А75х375",
        "unit": "шт",
        "min_quantity": 1,
        "price": 2500,
        "price_code": "roof_pvc_aerator_75x375_installation_item",
        "comment": "Добавлено по ответу Елены 2026-07-30: 587 руб. — материал аэратора, работа отдельно 2500 руб./шт.",
    },
    {
        "section": "Работы",
        "name": "Монтаж примыкания кровли из ПВХ мембраны",
        "unit": "мп",
        "min_quantity": 1,
        "price": 700,
        "price_code": "roof_pvc_membrane_abutment_work_m",
        "comment": "Добавлено 2026-08-02 по сверке эталонных смет: общее линейное примыкание кровли к парапетам/стенам/ВК считается в м.п.; отдельное примыкание к вентшахтам в шт остается optional legacy.",
    },
    {
        "section": "Работы",
        "name": "Вывоз мусора с объекта, контейнер/машина",
        "unit": "маш",
        "min_quantity": 1,
        "price": 10000,
        "price_code": "waste_removal_container_truck",
        "comment": "Перенесено из v3 и уточнено 2026-07-30: контейнер/машина идет в материальной колонке сметы.",
    },
]

SORT_BLOCK_ORDER = {
    "general": 0,
    "earthworks": 1,
    "concrete_sand": 2,
    "formwork_timber": 3,
    "insulation_thermal": 4,
    "waterproofing": 5,
    "walls_lintels": 6,
    "flat_roof": 7,
    "schiedel": 8,
    "other": 9,
}

SECTION_SORT_BLOCK = {
    "бетон": "concrete_sand",
    "песок": "concrete_sand",
    "пиломатериал": "formwork_timber",
    "арматура": "walls_lintels",
    "газобетон": "walls_lintels",
    "поротерм": "walls_lintels",
    "несущие стены и перемычки": "walls_lintels",
    "плоская кровля": "flat_roof",
    "кровельное покрытие дома": "flat_roof",
    "schiedel": "schiedel",
    "земляные работы": "earthworks",
    "устройство фундаментной плиты": "formwork_timber",
    "ж/б монолитная плита перекрытия 1-го этажа": "formwork_timber",
    "фундамент": "insulation_thermal",
}


def row_sort_block(row: list[Any]) -> str:
    section = normalize_text(row[REGISTRY_HEADERS.index("Раздел")])
    name = normalize_text(row[REGISTRY_HEADERS.index("Наименование")])
    code = normalize_text(row[REGISTRY_HEADERS.index("price_code")])

    text = f"{section} {name} {code}"
    if section in SECTION_SORT_BLOCK and section != "работы":
        return SECTION_SORT_BLOCK[section]
    if code in {
        "axis_marking_shift",
        "construction_camp_setup_item",
        "site_cabin_connection_item",
        "waste_removal_container_truck",
        "waste_removal_loading_work_truck",
    } or "строительный городок" in text or "бытовк" in text or "вынос осей" in text:
        return "general"
    if any(term in text for term in ("excavator", "землян", "грунт", "котлован", "геотекст", "песок", "коммуникац")):
        return "earthworks"
    if any(term in text for term in ("газобетон", "поротерм", "кладк", "перемыч", "парапет", "блок", "арматур", "lintel", "rebar")):
        return "walls_lintels"
    if any(term in text for term in ("бетон", "concrete", "насос", "миксер", "перенос, подъем бетона")):
        return "concrete_sand"
    if any(term in text for term in ("опалуб", "фанер", "пиломатериал", "timber", "plywood", "formwork")):
        return "formwork_timber"
    if any(term in text for term in ("утепл", "эппс", "eps", "термов", "пеноплэкс", "пеноплекс")):
        return "insulation_thermal"
    if any(term in text for term in ("гидроизоляц", "мастик", "битум", "planter", "waterproof")):
        return "waterproofing"
    if any(term in text for term in ("кров", "roof", "мембран", "воронк", "аэратор", "водосток", "пвх")):
        return "flat_roof"
    if "schiedel" in text or "вентканал" in text:
        return "schiedel"
    return SECTION_SORT_BLOCK.get(section, "other")


def sort_registry_rows(rows: list[list[Any]]) -> list[list[Any]]:
    indexed_rows = list(enumerate(rows))
    return [
        row
        for original_index, row in sorted(
            indexed_rows,
            key=lambda item: (
                SORT_BLOCK_ORDER[row_sort_block(item[1])],
                clean_text(item[1][REGISTRY_HEADERS.index("Раздел")]).lower(),
                item[0],
            ),
        )
    ]


def headers(ws) -> dict[str, int]:
    return {
        clean_text(ws.cell(1, column).value): column
        for column in range(1, ws.max_column + 1)
        if clean_text(ws.cell(1, column).value)
    }


def previous_code_index(path: Path) -> dict[tuple[str, str], set[str]]:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["price_registry"]
    header_map = headers(ws)
    index: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row, header_map["Наименование"]).value
        unit = ws.cell(row, header_map["Ед. изм."]).value
        code = clean_text(ws.cell(row, header_map["price_code"]).value)
        if name and unit and code:
            index[row_key(name, unit)].add(code)
    return index


def previous_registry_rows(path: Path) -> list[list[Any]]:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["price_registry"]
    header_map = headers(ws)
    rows: list[list[Any]] = []
    for row in range(2, ws.max_row + 1):
        if not clean_text(ws.cell(row, header_map["Наименование"]).value):
            continue
        rows.append([ws.cell(row, header_map[name]).value for name in REGISTRY_HEADERS])
    return rows


def deduplicate_rows_by_price_code(rows: list[list[Any]]) -> tuple[list[list[Any]], list[dict[str, Any]]]:
    code_index = REGISTRY_HEADERS.index("price_code")
    latest_by_code: dict[str, list[Any]] = {}
    first_position_by_code: dict[str, int] = {}
    uncoded_rows: list[list[Any]] = []
    duplicates: list[dict[str, Any]] = []

    for row in rows:
        code = clean_text(row[code_index])
        if not code:
            uncoded_rows.append(row)
            continue
        if code in latest_by_code:
            duplicates.append(
                {
                    "price_code": code,
                    "old_name": latest_by_code[code][REGISTRY_HEADERS.index("Наименование")],
                    "new_name": row[REGISTRY_HEADERS.index("Наименование")],
                }
            )
        else:
            first_position_by_code[code] = len(first_position_by_code)
        latest_by_code[code] = row

    coded_rows = sorted(
        latest_by_code.values(),
        key=lambda row: first_position_by_code[clean_text(row[code_index])],
    )
    return uncoded_rows + coded_rows, duplicates


def extract_work_price_rows(source_path: Path) -> list[dict[str, Any]]:
    wb = load_workbook(source_path, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows: list[dict[str, Any]] = []
    for row in range(3, ws.max_row + 1):
        name = ws.cell(row, 2).value
        unit = ws.cell(row, 3).value
        quantity = ws.cell(row, 4).value
        price = ws.cell(row, 5).value
        if not clean_text(name):
            continue
        rows.append(
            {
                "source_row": row,
                "section": "Работы",
                "name": clean_text(name),
                "unit": clean_text(unit),
                "min_quantity": quantity,
                "price": price,
            }
        )
    return rows


def build_registry_workbook(
    source_path: Path,
    previous_registry_path: Path,
    output_path: Path,
    archive_source_path: Path,
) -> dict[str, Any]:
    archive_source_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, archive_source_path)

    previous_codes = previous_code_index(previous_registry_path)
    source_rows = extract_work_price_rows(source_path)
    registry_rows = [
        row
        for row in previous_registry_rows(previous_registry_path)
        if clean_text(row[REGISTRY_HEADERS.index("price_code")]) not in OBSOLETE_PREVIOUS_PRICE_CODES
    ]
    merged_rows, removed_existing_duplicates = deduplicate_rows_by_price_code(registry_rows)

    wb = Workbook()
    ws = wb.active
    ws.title = "price_registry"
    ws.append(REGISTRY_HEADERS)

    matched = 0
    manual = 0
    ambiguous: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    ignored: list[dict[str, Any]] = []
    replaced_codes: set[str] = set()
    for item in source_rows:
        key = row_key(item["name"], item["unit"])
        if key in IGNORED_WORK_PRICE_ROWS:
            ignored.append(item)
            continue
        manual_code = MANUAL_WORK_PRICE_CODES.get(key)
        codes = sorted(previous_codes.get(key, set()))
        price_code = ""
        comment_parts = [f"Источник: первый лист нового прайса, строка {item['source_row']}."]
        if item["min_quantity"] not in (None, ""):
            comment_parts.append(f"Исходное кол-во: {item['min_quantity']}.")
        if manual_code:
            price_code = manual_code
            manual += 1
            comment_parts.append("price_code задан ручной картой normalize_elena_price_registry.py.")
        elif len(codes) == 1:
            price_code = codes[0]
            matched += 1
        elif len(codes) > 1:
            ambiguous.append({**item, "codes": codes})
            comment_parts.append(f"Неоднозначный price_code из v3: {', '.join(codes)}.")
        else:
            unmatched.append(item)
            comment_parts.append("price_code не найден автоматически: нужно сопоставить вручную.")

        new_row = [
            item["section"],
            PRICE_CODE_NAME_OVERRIDES.get(price_code, item["name"]),
            item["unit"],
            item["min_quantity"],
            item["price"],
            date.today().isoformat(),
            " ".join(comment_parts),
            price_code,
        ]
        if price_code:
            replaced = False
            for index, existing_row in enumerate(merged_rows):
                if clean_text(existing_row[REGISTRY_HEADERS.index("price_code")]) == price_code:
                    merged_rows[index] = new_row
                    replaced = True
                    replaced_codes.add(price_code)
                    break
            if not replaced:
                merged_rows.append(new_row)
                replaced_codes.add(price_code)
        else:
            merged_rows.append(new_row)

    for item in DERIVED_PRICE_ROWS:
        new_row = [
            item["section"],
            item["name"],
            item["unit"],
            item["min_quantity"],
            item["price"],
            date.today().isoformat(),
            item["comment"],
            item["price_code"],
        ]
        replaced = False
        for index, existing_row in enumerate(merged_rows):
            if clean_text(existing_row[REGISTRY_HEADERS.index("price_code")]) == item["price_code"]:
                merged_rows[index] = new_row
                replaced = True
                break
        if not replaced:
            merged_rows.append(new_row)
        replaced_codes.add(item["price_code"])

    final_rows, removed_final_duplicates = deduplicate_rows_by_price_code(merged_rows)
    final_rows = sort_registry_rows(final_rows)
    for row in final_rows:
        ws.append(row)

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9D9D9")
    ws.freeze_panes = "A2"
    widths = [22, 78, 14, 24, 14, 18, 80, 36]
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + index)].width = width

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {
        "source_path": source_path,
        "archive_source_path": archive_source_path,
        "output_path": output_path,
        "previous_registry_rows": len(registry_rows),
        "previous_unique_rows": len(merged_rows),
        "new_work_rows": len(source_rows),
        "matched": matched,
        "manual": manual,
        "replaced_codes": sorted(replaced_codes),
        "removed_existing_duplicates": removed_existing_duplicates,
        "removed_final_duplicates": removed_final_duplicates,
        "final_rows": len(final_rows),
        "ambiguous": ambiguous,
        "unmatched": unmatched,
        "ignored": ignored,
    }


def write_report(summary: dict[str, Any], report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Price Registry v4 Mapping Report",
        "",
        f"- Source file: `{summary['source_path']}`",
        f"- Archived source copy: `{summary['archive_source_path']}`",
        f"- Output registry: `{summary['output_path']}`",
        f"- Previous v3 registry rows copied: `{summary['previous_registry_rows']}`",
        f"- Previous duplicate price_code rows removed: `{len(summary['removed_existing_duplicates'])}`",
        f"- Work price rows from first sheet: `{summary['new_work_rows']}`",
        f"- Matched price_code from v3: `{summary['matched']}`",
        f"- Manual work price_code mappings: `{summary['manual']}`",
        f"- Existing price_code rows replaced by new price: `{len(summary['replaced_codes'])}`",
        f"- Final registry rows: `{summary['final_rows']}`",
        f"- Ambiguous matches: `{len(summary['ambiguous'])}`",
        f"- Unmatched rows: `{len(summary['unmatched'])}`",
        f"- Ignored source rows: `{len(summary['ignored'])}`",
        "",
    ]
    if summary["replaced_codes"]:
        lines.extend(["## Replaced price_code Rows", ", ".join(f"`{code}`" for code in summary["replaced_codes"]), ""])
    if summary["ambiguous"]:
        lines.extend(["## Ambiguous", "| source row | name | unit | candidate codes |", "|---:|---|---|---|"])
        for row in summary["ambiguous"]:
            lines.append(
                f"| {row['source_row']} | {row['name']} | {row['unit']} | {', '.join(row['codes'])} |"
            )
        lines.append("")
    if summary["unmatched"]:
        lines.extend(["## Unmatched", "| source row | name | unit | price |", "|---:|---|---|---:|"])
        for row in summary["unmatched"]:
            lines.append(f"| {row['source_row']} | {row['name']} | {row['unit']} | {row['price']} |")
        lines.append("")
    if summary["ignored"]:
        lines.extend(["## Ignored Source Rows", "| source row | name | unit | price | reason |", "|---:|---|---|---:|---|"])
        for row in summary["ignored"]:
            lines.append(
                f"| {row['source_row']} | {row['name']} | {row['unit']} | {row['price']} | "
                "Елена 2026-07-30: балки перекрытий считаем единой строкой по м.п. "
                "`beam_concrete_placing_work_m`; строку `м3 > 250мм` не используем. |"
            )
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--previous-registry", type=Path, default=DEFAULT_PREVIOUS_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--archive-source", type=Path, default=DEFAULT_ARCHIVE_SOURCE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    summary = build_registry_workbook(
        args.source,
        args.previous_registry,
        args.output,
        args.archive_source,
    )
    write_report(summary, args.report)
    print(
        "price_registry v4:",
        f"previous_rows={summary['previous_registry_rows']}",
        f"final_rows={summary['final_rows']}",
        f"new_work_rows={summary['new_work_rows']}",
        f"matched={summary['matched']}",
        f"manual={summary['manual']}",
        f"replaced={len(summary['replaced_codes'])}",
        f"ambiguous={len(summary['ambiguous'])}",
        f"unmatched={len(summary['unmatched'])}",
        f"ignored={len(summary['ignored'])}",
        f"output={summary['output_path']}",
    )


if __name__ == "__main__":
    main()
