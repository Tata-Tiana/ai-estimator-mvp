from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st

from excel_export import build_excel_bytes, save_excel
from report_export import build_markdown_report, save_markdown_report


APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[1]
OUTPUT_DIR = APP_DIR / "output"
REVIEW_CARD_PATH = (
    REPO_ROOT
    / "experiments"
    / "pdf_tests"
    / "projects"
    / "usv_yusupovo_village"
    / "merged"
    / "foundation_slab_review_card.json"
)
RESULT_CANDIDATES = [
    REPO_ROOT
    / "experiments"
    / "foundation_slab_calculator"
    / "cases"
    / "test_foundation_slab"
    / "foundation_slab_result.json",
    REPO_ROOT
    / "experiments"
    / "foundation_slab_calculator"
    / "output"
    / "test_foundation_slab"
    / "foundation_slab_result.json",
]

ADDRESS = (
    "Российская федерация, Московская область, г. о. Домодедово,<br>"
    'п. Государственного племенного завода "Константиново",<br>'
    "тер. КП &quot;Юсупово Виладж&quot;,<br>"
    "участок с кад. номером 50:28:0050421:2962"
)
SECTION_TITLE = "УСТРОЙСТВО ФУНДАМЕНТНОЙ ПЛИТЫ ДОМА, ТЕРРАСЫ, КРЫЛЬЦА (250мм, 300мм)"

ZERO_STRUCTURE_LINES = [
    {
        "code": "procurement_warehouse_costs_excel_structure",
        "name": "Заготовительно-складские расходы",
    },
    {
        "code": "overhead_general_business_costs_excel_structure",
        "name": "Накладные и общехозяйственные расходы",
    },
    {
        "code": "estimated_profit_excel_structure",
        "name": "Сметная прибыль",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def load_review_card() -> dict[str, Any]:
    return load_json(REVIEW_CARD_PATH)


def resolve_result_path() -> Path:
    for path in RESULT_CANDIDATES:
        if path.exists():
            return path
    matches = sorted(
        (
            REPO_ROOT
            / "experiments"
            / "foundation_slab_calculator"
        ).glob("**/foundation_slab_result.json")
    )
    if matches:
        return matches[-1]
    raise FileNotFoundError("foundation_slab_result.json not found")


@st.cache_data
def load_result() -> dict[str, Any]:
    result = load_json(resolve_result_path())
    return ensure_zero_structure_lines(result)


def zero_structure_line(code: str, name: str) -> dict[str, Any]:
    return {
        "code": code,
        "name": name,
        "unit": "-",
        "quantity": 1.0,
        "material_unit_price": 0.0,
        "material_total": 0,
        "work_unit_price": 0.0,
        "work_total": 0,
        "line_total": 0,
        "line_type": "zero_excel_structure_line",
    }


def ensure_zero_structure_lines(result: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(result, ensure_ascii=False))
    estimate_lines = result.setdefault("estimate_lines", [])
    existing_codes = {line.get("code") for line in estimate_lines}
    for item in ZERO_STRUCTURE_LINES:
        if item["code"] not in existing_codes:
            estimate_lines.append(zero_structure_line(item["code"], item["name"]))
    return result


def format_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric == 0:
        return "0"
    if numeric.is_integer():
        return f"{int(numeric):,}".replace(",", " ")
    text = f"{numeric:,.2f}".replace(",", " ")
    return text.rstrip("0").rstrip(".")


def quantity_for_display(line: dict[str, Any]) -> Any:
    return line.get("display_quantity", line.get("quantity"))


def parameter_rows(review_card: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in review_card.get("parameters", []):
        value = item.get("value")
        if isinstance(value, list):
            value = "; ".join(str(part) for part in value)
        rows.append(
            {
                "Параметр": item.get("label", ""),
                "Значение": value,
                "Ед.": item.get("unit", ""),
                "Источник": item.get("source_file", ""),
                "Страница": item.get("page", ""),
                "Статус": item.get("review_status", ""),
            }
        )
    return rows


def comparison_counts(result: dict[str, Any]) -> tuple[int, int]:
    comparison = result.get("comparison", [])
    if isinstance(comparison, dict):
        return int(comparison.get("ok_count", 0)), int(comparison.get("mismatch_count", 0))
    ok = sum(1 for item in comparison if item.get("status") == "ok")
    mismatch = sum(1 for item in comparison if item.get("status") != "ok")
    return ok, mismatch


def render_header() -> None:
    st.markdown(
        f"""
        <div class="demo-header">
          <div class="brand">Brick House</div>
          <div class="headline">СМЕТНЫЙ РАСЧЁТ НА СТРОИТЕЛЬСТВО ДОМА</div>
          <div class="address-label">Адрес:</div>
          <div class="address">{ADDRESS}</div>
          <div class="section-label">Раздел:</div>
          <div class="section">{SECTION_TITLE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_estimate_table(result: dict[str, Any]) -> None:
    totals = result.get("internal_totals", {})
    rows = []
    for index, line in enumerate(result.get("estimate_lines", []), start=1):
        qty = quantity_for_display(line)
        rows.append(
            "<tr>"
            f"<td class='num'>{index}</td>"
            f"<td class='name'>{html.escape(str(line.get('name', '')))}</td>"
            f"<td>{html.escape(str(line.get('unit', '')))}</td>"
            f"<td class='num'>{format_number(qty)}</td>"
            f"<td class='num'>{format_number(line.get('material_unit_price'))}</td>"
            f"<td class='num'>{format_number(line.get('material_total'))}</td>"
            f"<td class='num'>{format_number(line.get('work_unit_price'))}</td>"
            f"<td class='num'>{format_number(line.get('work_total'))}</td>"
            f"<td class='num'>{format_number(line.get('line_total'))}</td>"
            f"<td class='num grey split'>{format_number(qty)}</td>"
            f"<td class='num grey'>{format_number(line.get('material_unit_price'))}</td>"
            f"<td class='num grey'>{format_number(line.get('material_total'))}</td>"
            f"<td class='num grey'>{format_number(line.get('work_unit_price'))}</td>"
            f"<td class='num grey'>{format_number(line.get('work_total'))}</td>"
            f"<td class='num grey'>{format_number(line.get('line_total'))}</td>"
            "</tr>"
        )

    total_row = (
        "<tr class='total-row'>"
        "<td></td>"
        "<td>Итого по разделу:</td>"
        "<td></td>"
        "<td></td>"
        "<td></td>"
        f"<td class='num'>{format_number(totals.get('internal_materials_total'))}</td>"
        "<td></td>"
        f"<td class='num'>{format_number(totals.get('internal_works_total'))}</td>"
        f"<td class='num'>{format_number(totals.get('internal_section_total'))}</td>"
        "<td class='grey split'></td>"
        "<td class='grey'></td>"
        f"<td class='num grey'>{format_number(totals.get('internal_materials_total'))}</td>"
        "<td class='grey'></td>"
        f"<td class='num grey'>{format_number(totals.get('internal_works_total'))}</td>"
        f"<td class='num grey'>{format_number(totals.get('internal_section_total'))}</td>"
        "</tr>"
    )

    st.markdown(
        f"""
        <div class="estimate-wrap">
          <table class="estimate-table">
            <thead>
              <tr>
                <th rowspan="2">№</th>
                <th rowspan="2">Наименование работ</th>
                <th rowspan="2">Ед. изм.</th>
                <th rowspan="2">Кол-во</th>
                <th colspan="2">Стоимость материалов, машин и механизмов</th>
                <th colspan="2">Стоимость работ</th>
                <th rowspan="2">Итого</th>
                <th class="grey split" rowspan="2">Кол-во</th>
                <th class="grey" colspan="2">Стоимость материалов, машин и механизмов</th>
                <th class="grey" colspan="2">Стоимость работ</th>
                <th class="grey" rowspan="2">Итого</th>
              </tr>
              <tr>
                <th>цена</th>
                <th>сумма</th>
                <th>цена</th>
                <th>сумма</th>
                <th class="grey">цена</th>
                <th class="grey">сумма</th>
                <th class="grey">цена</th>
                <th class="grey">сумма</th>
              </tr>
            </thead>
            <tbody>
              {''.join(rows)}
              {total_row}
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def write_demo_files(review_card: dict[str, Any], result: dict[str, Any]) -> tuple[bytes, str, bytes]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    excel_path = OUTPUT_DIR / "usv_foundation_slab_demo.xlsx"
    report_path = OUTPUT_DIR / "usv_foundation_slab_demo_report.md"
    result_path = OUTPUT_DIR / "usv_foundation_slab_result.json"

    excel_bytes = save_excel(excel_path, result, SECTION_TITLE, ADDRESS.replace("<br>", "\n"))
    report_text = save_markdown_report(report_path, review_card, result, SECTION_TITLE)
    result_bytes = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
    result_path.write_bytes(result_bytes)
    return excel_bytes, report_text, result_bytes


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .demo-header {
            border: 1px solid #d7dde7;
            padding: 22px 26px;
            border-radius: 8px;
            background: #ffffff;
            margin-bottom: 18px;
        }
        .brand {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: .02em;
            color: #1e293b;
        }
        .headline {
            font-size: 20px;
            font-weight: 800;
            margin-top: 6px;
            color: #111827;
        }
        .address-label, .section-label {
            margin-top: 14px;
            font-weight: 700;
            color: #475569;
        }
        .address, .section {
            color: #111827;
            line-height: 1.45;
        }
        .section {
            font-weight: 800;
        }
        .estimate-wrap {
            overflow-x: auto;
            border: 1px solid #cfd6e4;
            border-radius: 6px;
        }
        .estimate-table {
            border-collapse: collapse;
            width: 100%;
            min-width: 1500px;
            font-size: 13px;
            background: #fff;
        }
        .estimate-table th, .estimate-table td {
            border: 1px solid #3f3f46;
            padding: 5px 7px;
            vertical-align: middle;
        }
        .estimate-table th {
            font-weight: 800;
            background: #f8fafc;
            text-align: center;
        }
        .estimate-table td.name {
            min-width: 360px;
            white-space: normal;
        }
        .estimate-table .num {
            text-align: right;
            white-space: nowrap;
        }
        .estimate-table .grey {
            background: #b7b7b7;
        }
        .estimate-table .split {
            border-left: 4px solid #1d4ed8;
        }
        .estimate-table .total-row td {
            font-weight: 800;
            background: #f8fafc;
        }
        .estimate-table .total-row td.grey {
            background: #a8a8a8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="AI-сметчик: демо по проекту ЮСВ", layout="wide")
    inject_css()
    st.title("AI-сметчик: демо по проекту ЮСВ")
    render_header()

    review_card = load_review_card()
    result = load_result()

    tab_project, tab_params, tab_estimate, tab_downloads = st.tabs(
        ["Проект", "Параметры из PDF", "Смета", "Скачать файлы"]
    )

    with tab_project:
        st.subheader("Проект")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("**Проект:** ЮСВ / Юсупово Виладж")
            st.write("**Источники:** КР-1, КР-2, АР")
            st.write("**Демо-раздел:** фундаментная плита")
        with col2:
            st.info(
                "AI/парсер извлекает параметры из PDF. "
                "Смету считает Python-калькулятор по формулам Елены. "
                "Клиентская часть в рамках demo не считается."
            )

    with tab_params:
        st.subheader("Параметры из PDF")
        st.dataframe(parameter_rows(review_card), use_container_width=True, hide_index=True)
        st.subheader("Что проверить Елене")
        for question in review_card.get("review_questions_for_elena", []):
            st.write(f"- {question}")

    with tab_estimate:
        st.subheader("Смета фундаментной плиты")
        totals = result.get("internal_totals", {})
        ok_count, mismatch_count = comparison_counts(result)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Материалы / механизмы", format_number(totals.get("internal_materials_total")))
        c2.metric("Работы", format_number(totals.get("internal_works_total")))
        c3.metric("Итого", format_number(totals.get("internal_section_total")))
        c4.metric("Проверка", f"{ok_count} ok / {mismatch_count} mismatch")
        st.caption("Белая зона является технической копией серой зоны. Клиентские коэффициенты не применяются.")
        render_estimate_table(result)

        warnings = result.get("warnings", [])
        if warnings:
            st.warning("\n".join(f"- {warning}" for warning in warnings))

    with tab_downloads:
        st.subheader("Скачать файлы")
        excel_bytes, report_text, result_bytes = write_demo_files(review_card, result)
        d1, d2, d3 = st.columns(3)
        d1.download_button(
            "Скачать Excel",
            data=excel_bytes,
            file_name="usv_foundation_slab_demo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        d2.download_button(
            "Скачать расчётный отчёт",
            data=report_text,
            file_name="usv_foundation_slab_demo_report.md",
            mime="text/markdown",
        )
        d3.download_button(
            "Скачать result.json",
            data=result_bytes,
            file_name="usv_foundation_slab_result.json",
            mime="application/json",
        )
        st.write("Файлы также сохраняются локально в `experiments/demo_usv_app/output/`.")


if __name__ == "__main__":
    main()
