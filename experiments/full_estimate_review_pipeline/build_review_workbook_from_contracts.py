from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = ROOT / "experiments" / "full_estimate_review_pipeline"
DEFAULT_OUTPUT = PIPELINE_DIR / "output" / "step_06_earthworks_waterproofing_review.xlsx"

FONT_NAME = "Arial"
FILL_HEADER = PatternFill("solid", fgColor="D9D9D9")
FILL_SECTION = PatternFill("solid", fgColor="F4CCCC")
FILL_INPUT = PatternFill("solid", fgColor="D9EAD3")
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
    "Раздел",
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
    "Раздел",
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
    "Раздел",
    "Таблица",
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
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(ws.max_column)}{ws.max_row}"
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
        cell.font = Font(name=FONT_NAME, bold=True, size=10)


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


def build_constructor_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.active
    ws.title = "00_Конструктор сметы"
    headers = [
        "Раздел сметы",
        "Код раздела",
        "Включить в смету",
        "Статус готовности",
        "Строк проверки",
        "Цены",
        "Детализации",
        "Строк сметы",
        "Комментарий",
    ]
    ws.append(headers)
    for contract in contracts:
        ws.append([
            section_name(contract),
            section_code(contract),
            "да",
            contract["section"].get("status", ""),
            len(contract.get("review_parameters") or []),
            len(contract.get("price_keys") or []),
            len(contract.get("detail_tables") or []),
            len(contract.get("estimate_lines") or []),
            contract["section"].get("owner_notes", ""),
        ])

    validation = DataValidation(type="list", formula1='"да,нет"', allow_blank=False)
    ws.add_data_validation(validation)
    validation.add(f"C2:C{ws.max_row}")
    apply_table_style(ws)
    set_widths(ws, {
        "A": 34,
        "B": 24,
        "C": 16,
        "D": 20,
        "E": 14,
        "F": 10,
        "G": 14,
        "H": 12,
        "I": 72,
    })


def build_project_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("01_Проверка проекта")
    ws.append(["Review workbook: проектные входы из section contracts", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append([
        "Проверочный лист",
        "Значения здесь должны приходить из parser/chat JSON или ручной правки.",
        "",
        "",
        "",
        "",
        "",
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
        append_section_band(ws, [section_name(contract), section_code(contract)], len(PROJECT_HEADERS))
        for param in contract.get("review_parameters") or []:
            review_behavior = param.get("review_behavior") or {}
            ws.append([
                section_name(contract),
                param.get("label_ru", param.get("key", "")),
                None,
                param.get("unit", ""),
                "Ожидает извлечения",
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
    ws.freeze_panes = "A5"
    set_widths(ws, {
        "A": 30,
        "B": 38,
        "C": 20,
        "D": 10,
        "E": 20,
        "F": 62,
        "G": 36,
        "H": 58,
        "I": 28,
        "J": 28,
        "K": 20,
        "L": 28,
        "M": 18,
        "N": 24,
    })
    for column in ["K", "L", "M", "N"]:
        ws.column_dimensions[column].hidden = True


def build_prices_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("02_Цены себестоимости")
    ws.append(PRICE_HEADERS)
    for contract in contracts:
        append_section_band(ws, [section_name(contract), section_code(contract)], len(PRICE_HEADERS))
        for price in contract.get("price_keys") or []:
            ws.append([
                section_name(contract),
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
    set_widths(ws, {
        "A": 30,
        "B": 42,
        "C": 22,
        "D": 12,
        "E": 16,
        "F": 16,
        "G": 18,
        "H": 18,
        "I": 30,
        "J": 16,
        "K": 58,
        "L": 20,
        "M": 30,
        "N": 30,
        "O": 30,
        "P": 22,
    })
    for column in ["L", "M", "N", "O", "P"]:
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
        section_name(contract),
        table.get("label_ru", table.get("key", "")),
        "Шаблон строк",
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


def build_details_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("03_Детали объемов")
    ws.append(DETAIL_HEADERS)
    for contract in contracts:
        tables = contract.get("detail_tables") or []
        if not tables:
            continue
        append_section_band(ws, [section_name(contract), section_code(contract)], len(DETAIL_HEADERS))
        for table in tables:
            ws.append(detail_template_row(contract, table))
            for cell in ws[ws.max_row]:
                cell.fill = FILL_DETAIL

    apply_table_style(ws)
    set_widths(ws, {
        "A": 30,
        "B": 30,
        "C": 18,
        "D": 34,
        "E": 16,
        "F": 16,
        "G": 16,
        "H": 16,
        "I": 16,
        "J": 18,
        "K": 14,
        "L": 18,
        "M": 14,
        "N": 34,
        "O": 54,
        "P": 24,
        "Q": 20,
        "R": 26,
    })
    for column in ["Q", "R"]:
        ws.column_dimensions[column].hidden = True


def build_instruction_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("04_Инструкция")
    ws.append(["Раздел", "Инструкция"])
    rows = [
        ("00", "Выберите разделы, которые входят в смету."),
        ("01", "Проверьте проектные параметры. Пустые значения должны быть заполнены parser/chat JSON или вручную."),
        ("02", "Проверьте себестоимость. Цена для расчета должна прийти из price registry, fallback или ручной правки."),
        ("03", "Проверьте детальные таблицы. Это проектные строки, а не строки финальной сметы."),
        ("05", "Технический лист показывает, из каких контрактов собрана таблица."),
        ("06", "Raw contracts нужен разработчику для диагностики структуры."),
    ]
    for row in rows:
        ws.append(row)
    apply_table_style(ws)
    set_widths(ws, {"A": 14, "B": 120})


def build_contracts_summary_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("05_Контракты")
    ws.append([
        "section_code",
        "section_name",
        "review_parameters",
        "price_keys",
        "detail_tables",
        "defaults",
        "auto_calculated",
        "estimate_lines",
        "source_files",
    ])
    for contract in contracts:
        ws.append([
            section_code(contract),
            section_name(contract),
            len(contract.get("review_parameters") or []),
            len(contract.get("price_keys") or []),
            len(contract.get("detail_tables") or []),
            len(contract.get("defaults") or []),
            len(contract.get("auto_calculated") or []),
            len(contract.get("estimate_lines") or []),
            json.dumps(contract.get("source_files") or {}, ensure_ascii=False),
        ])
    apply_table_style(ws)
    set_widths(ws, {
        "A": 24,
        "B": 34,
        "C": 18,
        "D": 12,
        "E": 14,
        "F": 10,
        "G": 16,
        "H": 14,
        "I": 100,
    })
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.fill = FILL_TECH


def build_raw_contracts_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("06_Raw contracts")
    ws.append(["section_code", "block", "json"])
    for contract in contracts:
        for block in [
            "section",
            "review_parameters",
            "price_keys",
            "detail_tables",
            "defaults",
            "auto_calculated",
            "estimate_lines",
        ]:
            ws.append([
                section_code(contract),
                block,
                json.dumps(contract.get(block), ensure_ascii=False, indent=2),
            ])
    apply_table_style(ws)
    set_widths(ws, {"A": 24, "B": 24, "C": 120})
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.fill = FILL_TECH


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
        if cell_text(ws_project.cell(row_idx, 12).value):
            project_rows += 1

    price_rows = 0
    for row_idx in range(2, ws_prices.max_row + 1):
        if cell_text(ws_prices.cell(row_idx, 13).value):
            price_rows += 1

    detail_template_rows = 0
    for row_idx in range(2, ws_details.max_row + 1):
        if cell_text(ws_details.cell(row_idx, 18).value):
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
