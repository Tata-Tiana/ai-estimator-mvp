from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation


ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = ROOT / "experiments" / "full_estimate_review_pipeline"
DEFAULT_OUTPUT = PIPELINE_DIR / "output" / "step_07_earthworks_waterproofing_schiedel_review.xlsx"

FONT_NAME = "Arial"
FILL_HEADER = PatternFill("solid", fgColor="D9D9D9")
FILL_SECTION = PatternFill("solid", fgColor="E7E6E6")
FILL_FOUND = PatternFill("solid", fgColor="D9EAD3")
FILL_REVIEW = PatternFill("solid", fgColor="FCE4D6")
FILL_MISSING = PatternFill("solid", fgColor="F4CCCC")
FILL_INPUT = FILL_REVIEW
FILL_PRICE = PatternFill("solid", fgColor="D9EAD3")
FILL_DETAIL = PatternFill("solid", fgColor="DAE8FC")
FILL_TECH = PatternFill("solid", fgColor="E7E6E6")
FILL_WHITE = PatternFill("solid", fgColor="FFFFFF")
BORDER_THIN = Border(
    left=Side(style="thin", color="B7B7B7"),
    right=Side(style="thin", color="B7B7B7"),
    top=Side(style="thin", color="B7B7B7"),
    bottom=Side(style="thin", color="B7B7B7"),
)

PROJECT_HEADERS = [
    "Что проверяем",
    "Найдено в проекте",
    "Ед.",
    "Статус",
    "Что нужно сделать",
    "Источник",
    "Фрагмент проекта",
    "Исправить / ввести значение",
    "Комментарий Елены",
    "section_code",
    "technical_key",
    "source_class",
    "target_code",
]

PRICE_HEADERS = [
    "Строка сметы",
    "Что это за цена",
    "Ед.",
    "Цена из прайса",
    "Цена fallback",
    "Цена для расчета",
    "Исправить цену",
    "Источник цены",
    "Нужно внимание",
    "Комментарий",
    "section_code",
    "calc_price_key",
    "price_registry_code",
    "fallback_key",
    "selected_price_source",
]

DETAIL_HEADERS = [
    "Тип",
    "Наименование",
    "Длина, м",
    "Глубина, м",
    "Ширина, м",
    "Объем, м3",
    "Диаметр, мм",
    "Длина одной, м",
    "Количество",
    "Итоговая длина, м",
    "Включено",
    "Источник",
    "Фрагмент проекта",
    "Комментарий Елены",
    "section_code",
    "detail_table_key",
]

CANONICAL_SECTIONS = [
    ("earthworks", "Земляные работы"),
    ("foundation_slab", "Фундаментная плита"),
    ("waterproofing", "Гидроизоляция"),
    ("load_bearing_walls_lintels", "Стены и перемычки"),
    ("floor_slab_1", "Перекрытие 1 этажа"),
    ("floor_slab_2", "Перекрытие 2 этажа"),
    ("flat_roof", "Кровля"),
    ("schiedel_vent_channels", "Schiedel / вентканалы"),
]

GENERIC_DETAIL_TEMPLATES = [
    {
        "title": "Арматура",
        "detail_table_key": "rebar_items",
        "type": "Арматура",
        "name": "Марка / позиция арматуры",
        "diameter": "Диаметр, мм",
        "length_one": "Длина, м/п",
        "quantity": "Количество",
        "total_length": "Итоговая длина, м/п",
        "fragment": "Для foundation/floor slabs/load-bearing/lintels: spec_length_m является первичной единицей, если PDF дает м/п.",
    },
    {
        "title": "Балки",
        "detail_table_key": "beam_items",
        "type": "Балка",
        "name": "Балка / позиция",
        "length": "Длина, м",
        "depth": "Высота, м",
        "width": "Ширина, м",
        "quantity": "Количество",
        "fragment": "Для плит перекрытия с балками: геометрия балки и/или строка спецификации Ж/Б балок.",
    },
    {
        "title": "Перемычки",
        "detail_table_key": "lintel_items",
        "type": "Перемычка",
        "name": "Перемычка / U-блок",
        "length": "Длина, м",
        "quantity": "Количество",
        "total_length": "Итоговая длина, м",
        "fragment": "Для load_bearing_walls_lintels: длины перемычек и арматуры перемычек.",
    },
    {
        "title": "Вентканалы / сегменты",
        "detail_table_key": "vent_chimney_cladding_segments",
        "type": "Вентканал",
        "name": "Сегмент / канал",
        "length": "Длина, м",
        "quantity": "Количество",
        "fragment": "Для Schiedel и обкладки вентканалов, если PDF дает повторяющиеся сегменты.",
    },
    {
        "title": "Спецификация материалов",
        "detail_table_key": "material_spec_rows",
        "type": "Материал",
        "name": "Материал / строка спецификации",
        "volume": "Объем, м3",
        "quantity": "Количество",
        "fragment": "Для ЭППС, бетона, опалубки, мембран и других строк спецификаций, которые не являются отдельной геометрией.",
    },
    {
        "title": "Сырые строки таблиц",
        "detail_table_key": "raw_table_rows",
        "type": "Raw row",
        "name": "Сырая строка PDF",
        "fragment": "Raw table row from chat extraction before mapping to target_code.",
    },
]


def load_yaml_contract(path: Path) -> dict[str, Any]:
    ruby = (
        "require 'yaml'; require 'json'; "
        "puts JSON.generate(YAML.load_file(ARGV[0]))"
    )
    result = subprocess.run(
        ["ruby", "-e", ruby, str(path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def default_contract_paths() -> list[Path]:
    return [
        PIPELINE_DIR / "sections" / "earthworks" / "section_contract.yaml",
        PIPELINE_DIR / "sections" / "waterproofing" / "section_contract.yaml",
        PIPELINE_DIR / "sections" / "schiedel_vent_channels" / "section_contract.yaml",
    ]


def cell_text(value: Any) -> str:
    return "" if value is None else str(value)


def style_header_row(ws, row_idx: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        cell = ws.cell(row_idx, col)
        cell.font = Font(name=FONT_NAME, bold=True, size=10)
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER_THIN


def apply_table_style(ws, header_row: int = 1) -> None:
    style_header_row(ws, header_row, ws.max_column)
    ws.freeze_panes = f"A{header_row + 1}"
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.font = Font(name=FONT_NAME, bold=cell.font.bold, size=cell.font.sz or 10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER_THIN


def set_widths(ws, widths: dict[str, float]) -> None:
    for column, width in widths.items():
        ws.column_dimensions[column].width = width


def append_section_band(ws, row_values: list[Any], max_col: int) -> None:
    ws.append(row_values + [""] * max(0, max_col - len(row_values)))
    row_idx = ws.max_row
    for cell in ws[row_idx]:
        cell.fill = FILL_SECTION
        cell.font = Font(name=FONT_NAME, bold=True, color="000000", size=10)


def restyle_section_bands(ws) -> None:
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        if row[0].fill.fgColor.rgb == "00E7E6E6":
            for cell in row:
                cell.fill = FILL_SECTION
                cell.font = Font(name=FONT_NAME, bold=True, color="000000", size=10)


def style_block_title_row(ws, row_idx: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        cell = ws.cell(row_idx, col)
        cell.fill = FILL_TECH
        cell.font = Font(name=FONT_NAME, bold=True, color="000000", size=10)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER_THIN


def append_block(ws, title: str, headers: list[str], rows: list[list[Any]]) -> None:
    if ws.max_row == 1 and not ws.cell(1, 1).value:
        ws.cell(1, 1).value = title
    else:
        ws.append([])
        ws.append([title])
    style_block_title_row(ws, ws.max_row, max(len(headers), 1))
    ws.append(headers)
    style_header_row(ws, ws.max_row, len(headers))
    for row in rows:
        ws.append(row)


def restyle_block_sheet(ws) -> None:
    for row_idx in range(1, ws.max_row + 1):
        first_value = cell_text(ws.cell(row_idx, 1).value)
        if first_value.startswith("Блок "):
            style_block_title_row(ws, row_idx, ws.max_column)
            if row_idx + 1 <= ws.max_row:
                style_header_row(ws, row_idx + 1, ws.max_column)


def block_header_rows(ws) -> set[int]:
    rows = set()
    for row_idx in range(1, ws.max_row + 1):
        if cell_text(ws.cell(row_idx, 1).value).startswith("Блок ") and row_idx + 1 <= ws.max_row:
            rows.add(row_idx + 1)
    return rows


def section_name(contract: dict[str, Any]) -> str:
    return contract["section"]["name_ru"]


def section_code(contract: dict[str, Any]) -> str:
    return contract["section"]["code"]


def price_role_ru(price_kind: str) -> str:
    return {
        "work": "Работа",
        "material": "Материал",
        "fixed": "Фиксированная строка",
    }.get(price_kind, price_kind)


def review_rows_for_contract(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return (contract.get("review_parameters") or []) + (contract.get("supplier_inputs") or [])


def build_constructor_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.active
    ws.title = "00_Конструктор сметы"
    contracts_by_code = {section_code(contract): contract for contract in contracts}
    headers = [
        "Раздел сметы",
        "Код раздела",
        "Включить в смету",
        "Статус готовности",
        "Что сейчас проверяется",
        "Комментарий",
    ]
    ws.append(headers)
    for code, name in CANONICAL_SECTIONS:
        contract = contracts_by_code.get(code)
        enabled = "да" if contract is not None else "нет"
        status = contract["section"].get("status", "") if contract else "позже"
        current_check = ""
        comment = ""
        if contract:
            current_check = "проверка проектных данных, цен и деталей"
            comment = (
                f"строки проверки: {len(review_rows_for_contract(contract))}; "
                f"цены: {len(contract.get('price_keys') or [])}; "
                f"детали: {len(contract.get('detail_tables') or [])}"
            )
        ws.append([
            name,
            code,
            enabled,
            status,
            current_check,
            comment,
        ])

    validation = DataValidation(type="list", formula1='"да,нет"', allow_blank=False)
    ws.add_data_validation(validation)
    validation.add(f"C2:C{ws.max_row}")
    apply_table_style(ws)
    set_widths(ws, {
        "A": 22,
        "B": 22,
        "C": 22,
        "D": 24,
        "E": 44,
        "F": 80,
    })


def build_project_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("01_Проверка проекта")
    ws.append(["Разбор проекта:\nземляные работы + гидроизоляция + Schiedel", "", "", "", "", "", "", "", "", "", "", "", ""])
    review_count = sum(len(review_rows_for_contract(contract)) for contract in contracts)
    ws.append([
        "Найдено уверенно: 0",
        f"Проверьте: {review_count}",
        "Не найдено: 0",
        "Ручной ввод: 0",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ])
    ws.append([])
    ws.append(PROJECT_HEADERS)

    for contract in contracts:
        append_section_band(ws, [section_name(contract)], len(PROJECT_HEADERS))
        for param in review_rows_for_contract(contract):
            review_behavior = param.get("review_behavior") or {}
            ws.append([
                param.get("label_ru", param.get("key", "")),
                None,
                param.get("unit", ""),
                "Проверьте",
                review_behavior.get("action_ru", "Проверьте значение."),
                "",
                "",
                "",
                "",
                section_code(contract),
                param.get("key", ""),
                param.get("source_class", ""),
                param.get("target_code", ""),
            ])
            for cell in ws[ws.max_row]:
                cell.fill = FILL_INPUT

    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=13)
    ws.cell(1, 1).fill = FILL_HEADER
    apply_table_style(ws, header_row=4)
    restyle_section_bands(ws)
    ws.freeze_panes = "A5"
    set_widths(ws, {
        "A": 30,
        "B": 22,
        "C": 10,
        "D": 16,
        "E": 62,
        "F": 48,
        "G": 64,
        "H": 28,
        "I": 28,
        "J": 20,
        "K": 28,
        "L": 18,
        "M": 24,
    })
    for column in ["J", "K", "L", "M"]:
        ws.column_dimensions[column].hidden = True


def build_prices_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("02_Цены себестоимости")
    ws.append(PRICE_HEADERS)
    for contract in contracts:
        append_section_band(ws, [section_name(contract)], len(PRICE_HEADERS))
        for price in contract.get("price_keys") or []:
            ws.append([
                price.get("label_ru", ""),
                price_role_ru(str(price.get("price_kind", ""))),
                price.get("unit", ""),
                None,
                None,
                None,
                "",
                price.get("default_source", ""),
                "да",
                "Заполнить цену из price registry/fallback/review.",
                section_code(contract),
                price.get("key", ""),
                price.get("registry_code", ""),
                price.get("fallback_key", ""),
                "",
            ])
            for cell in ws[ws.max_row]:
                cell.fill = FILL_PRICE

    apply_table_style(ws)
    restyle_section_bands(ws)
    set_widths(ws, {
        "A": 38,
        "B": 24,
        "C": 10,
        "D": 16,
        "E": 16,
        "F": 18,
        "G": 18,
        "H": 38,
        "I": 16,
        "J": 66,
        "K": 20,
        "L": 30,
        "M": 30,
        "N": 30,
        "O": 22,
    })
    for column in ["K", "L", "M", "N", "O"]:
        ws.column_dimensions[column].hidden = True


def detail_template_row(contract: dict[str, Any], table: dict[str, Any]) -> list[Any]:
    columns = {item.get("key"): item for item in table.get("columns") or []}
    def label(key: str) -> str:
        item = columns.get(key)
        if not item:
            return ""
        unit = item.get("unit") or ""
        return f"{item.get('label_ru', key)}{', ' + unit if unit else ''}"

    return [
        table.get("label_ru", table.get("key", "")),
        label("name") or "Наименование",
        label("length_m"),
        label("depth_m"),
        label("width_m"),
        label("volume_m3"),
        label("diameter_mm"),
        label("pipe_length_m"),
        label("quantity"),
        label("total_length_m"),
        label("include_in_communications"),
        "",
        "",
        "",
        section_code(contract),
        table.get("key", ""),
    ]


def generic_detail_row(template: dict[str, Any]) -> list[Any]:
    return [
        template.get("type", ""),
        template.get("name", ""),
        template.get("length", ""),
        template.get("depth", ""),
        template.get("width", ""),
        template.get("volume", ""),
        template.get("diameter", ""),
        template.get("length_one", ""),
        template.get("quantity", ""),
        template.get("total_length", ""),
        "",
        "",
        template.get("fragment", ""),
        "",
        "template",
        template.get("detail_table_key", ""),
    ]


def build_details_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("03_Детали объемов")
    ws.append(DETAIL_HEADERS)
    has_detail_block = False
    for contract in contracts:
        tables = contract.get("detail_tables") or []
        if not tables:
            continue
        if has_detail_block:
            ws.append([])
        append_section_band(ws, [section_name(contract)], len(DETAIL_HEADERS))
        has_detail_block = True
        for table in tables:
            ws.append(detail_template_row(contract, table))
            for cell in ws[ws.max_row]:
                cell.fill = FILL_WHITE
    if has_detail_block:
        ws.append([])
    append_section_band(ws, ["Будущие detail-шаблоны"], len(DETAIL_HEADERS))
    for template in GENERIC_DETAIL_TEMPLATES:
        ws.append([])
        append_section_band(ws, [template["title"]], len(DETAIL_HEADERS))
        ws.append(generic_detail_row(template))
        for cell in ws[ws.max_row]:
            cell.fill = FILL_WHITE

    apply_table_style(ws)
    restyle_section_bands(ws)
    set_widths(ws, {
        "A": 18,
        "B": 44,
        "C": 14,
        "D": 14,
        "E": 14,
        "F": 16,
        "G": 16,
        "H": 18,
        "I": 14,
        "J": 18,
        "K": 14,
        "L": 44,
        "M": 78,
        "N": 24,
        "O": 20,
        "P": 26,
    })
    for column in ["O", "P"]:
        ws.column_dimensions[column].hidden = True


def build_instruction_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("04_Инструкция")
    ws.append(["Раздел", "Инструкция"])
    rows = [
        (0, "Выберите разделы, которые входят в смету."),
        (1, "Проверьте проектные параметры. Пустые значения должны быть заполнены parser/chat JSON или вручную."),
        (2, "Проверьте себестоимость. Цена для расчета должна прийти из price registry, fallback или ручной правки."),
        (3, "Проверьте детальные таблицы. Это проектные строки, а не строки финальной сметы."),
        (5, "Технический лист показывает, из каких контрактов собрана таблица."),
        (6, "Сырые данные parser нужны разработчику для диагностики структуры."),
    ]
    for row in rows:
        ws.append(row)
    apply_table_style(ws)
    set_widths(ws, {"A": 8, "B": 120})


def build_contracts_summary_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("05_Кандидаты parser")
    total_review = sum(len(review_rows_for_contract(contract)) for contract in contracts)
    total_prices = sum(len(contract.get("price_keys") or []) for contract in contracts)
    total_detail = sum(len(contract.get("detail_tables") or []) for contract in contracts)
    total_defaults = sum(len(contract.get("defaults") or []) for contract in contracts)
    total_auto = sum(len(contract.get("auto_calculated") or []) for contract in contracts)

    append_block(
        ws,
        "Блок 0: Summary запуска",
        ["Показатель", "Значение", "Комментарий"],
        [
            ["source", "section_contracts", "workbook собран локально из section_contract.yaml"],
            ["sections_count", len(contracts), "сколько section contracts загружено"],
            ["review_rows_count", total_review, "сколько строк проверки проекта, включая supplier/manual inputs"],
            ["price_rows_count", total_prices, "сколько строк цен"],
            ["detail_templates_count", total_detail + len(GENERIC_DETAIL_TEMPLATES), "сколько detail-шаблонов"],
            ["defaults_count", total_defaults, "числовые default/ручные параметры остаются в contracts"],
            ["auto_calculated_count", total_auto, "поля, которые должны считаться кодом, а не извлекаться из PDF"],
            ["parser_candidates_connected", "нет", "будет заполнено на шаге extraction JSON -> workbook"],
        ],
    )

    contract_rows = []
    for contract in contracts:
        contract_rows.append([
            section_code(contract),
            section_name(contract),
            len(review_rows_for_contract(contract)),
            len(contract.get("price_keys") or []),
            len(contract.get("detail_tables") or []),
            len(contract.get("supplier_inputs") or []),
            len(contract.get("defaults") or []),
            len(contract.get("auto_calculated") or []),
            len(contract.get("estimate_lines") or []),
            json.dumps(contract.get("source_files") or {}, ensure_ascii=False),
        ])
    append_block(
        ws,
        "Блок 1: section contracts",
        [
            "section_code",
            "section_name",
            "review_rows",
            "price_keys",
            "detail_tables",
            "supplier_inputs",
            "defaults",
            "auto_calculated",
            "estimate_lines",
            "source_files",
        ],
        contract_rows,
    )

    detail_rows = []
    for contract in contracts:
        for table in contract.get("detail_tables") or []:
            detail_rows.append([
                table.get("key", ""),
                table.get("label_ru", ""),
                "contract",
                section_code(contract),
                "детальная таблица уже описана в section_contract.yaml",
            ])
    for template in GENERIC_DETAIL_TEMPLATES:
        detail_rows.append([
            template.get("detail_table_key", ""),
            template.get("title", ""),
            template.get("type", ""),
            "future sections",
            template.get("fragment", ""),
        ])
    append_block(
        ws,
        "Блок 2: planned detail groups",
        ["detail_table_key", "title", "type", "used_for", "comment"],
        detail_rows,
    )

    apply_table_style(ws)
    restyle_block_sheet(ws)
    set_widths(ws, {
        "A": 24,
        "B": 34,
        "C": 28,
        "D": 22,
        "E": 34,
        "F": 18,
        "G": 22,
        "H": 18,
        "I": 18,
        "J": 100,
    })
    header_rows = block_header_rows(ws)
    for row in ws.iter_rows(min_row=1):
        for cell in row:
            if not cell_text(ws.cell(cell.row, 1).value).startswith("Блок ") and cell.row not in header_rows:
                cell.fill = FILL_WHITE


def build_raw_contracts_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("06_Сырые данные parser")
    append_block(
        ws,
        "Блок 0: Summary запуска",
        ["Показатель", "Значение", "Комментарий"],
        [
            ["source", "section_contracts", "сырые parser/chat данные подключаются следующим шагом"],
            ["sections_count", len(contracts), "сколько section contracts загружено"],
            ["raw_parser_json_connected", "нет", "пока лист показывает сырье contracts для диагностики"],
        ],
    )
    raw_rows = []
    for contract in contracts:
        for block in [
            "section",
            "review_parameters",
            "price_keys",
            "detail_tables",
            "supplier_inputs",
            "defaults",
            "auto_calculated",
            "estimate_lines",
        ]:
            raw_rows.append([
                section_code(contract),
                block,
                json.dumps(contract.get(block), ensure_ascii=False, indent=2),
            ])
    append_block(ws, "Блок 1: raw contract blocks", ["section_code", "block", "json"], raw_rows)
    apply_table_style(ws)
    restyle_block_sheet(ws)
    set_widths(ws, {"A": 24, "B": 24, "C": 120})
    header_rows = block_header_rows(ws)
    for row in ws.iter_rows(min_row=1):
        for cell in row:
            if not cell_text(ws.cell(cell.row, 1).value).startswith("Блок ") and cell.row not in header_rows:
                cell.fill = FILL_WHITE


def build_workbook(contract_paths: list[Path], output_path: Path) -> dict[str, Any]:
    contracts = [load_yaml_contract(path) for path in contract_paths]
    wb = Workbook()
    build_constructor_sheet(wb, contracts)
    build_project_sheet(wb, contracts)
    build_prices_sheet(wb, contracts)
    build_details_sheet(wb, contracts)
    build_instruction_sheet(wb)
    build_contracts_summary_sheet(wb, contracts)
    build_raw_contracts_sheet(wb, contracts)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    check = inspect_workbook(output_path)
    check["output_path"] = str(output_path)
    check["contracts"] = [str(path) for path in contract_paths]
    return check


def inspect_workbook(path: Path) -> dict[str, Any]:
    wb = load_workbook(path, data_only=False)
    sheets = wb.sheetnames
    ws_project = wb["01_Проверка проекта"]
    ws_prices = wb["02_Цены себестоимости"]
    ws_details = wb["03_Детали объемов"]

    project_rows = 0
    for row_idx in range(5, ws_project.max_row + 1):
        if cell_text(ws_project.cell(row_idx, 11).value):
            project_rows += 1

    price_rows = 0
    for row_idx in range(2, ws_prices.max_row + 1):
        if cell_text(ws_prices.cell(row_idx, 12).value):
            price_rows += 1

    detail_template_rows = 0
    for row_idx in range(2, ws_details.max_row + 1):
        if cell_text(ws_details.cell(row_idx, 16).value):
            detail_template_rows += 1

    return {
        "sheet_names": sheets,
        "project_parameter_rows": project_rows,
        "price_rows": price_rows,
        "detail_template_rows": detail_template_rows,
        "project_max_row": ws_project.max_row,
        "price_max_row": ws_prices.max_row,
        "details_max_row": ws_details.max_row,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        action="append",
        dest="contracts",
        help="Path to section_contract.yaml. Can be passed multiple times.",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contract_paths = [Path(item) for item in args.contracts] if args.contracts else default_contract_paths()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    check = build_workbook(contract_paths, output_path)
    if args.json:
        print(json.dumps(check, ensure_ascii=False, indent=2))
    else:
        print(f"built: {check['output_path']}")
        print(f"sheets: {', '.join(check['sheet_names'])}")
        print(f"project_parameter_rows: {check['project_parameter_rows']}")
        print(f"price_rows: {check['price_rows']}")
        print(f"detail_template_rows: {check['detail_template_rows']}")


if __name__ == "__main__":
    main()
