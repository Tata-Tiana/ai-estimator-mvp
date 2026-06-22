from __future__ import annotations

import json
from pathlib import Path

from openpyxl import load_workbook


FORBIDDEN_SOURCE_STRINGS = [
    "merge_rows_to_price_registry",
    "publish_canonical_registry",
    "normalize_price_registry_sheet",
]

# Drawing titles that legitimately contain communication pipe specs.
# Different projects name this sheet differently.
VALID_COMMUNICATION_SCHEME_TITLES = {
    "Схема коммуникаций",
    "Схема ввода инженерных сетей",
    "Схема инженерных сетей",
    "Схема наружных инженерных сетей",
    "Схема наружных сетей",
}

EXPECTED_05_HEADERS = [
    "Параметр",
    "technical_key",
    "Значение кратко",
    "Ед.",
    "Статус кандидата",
    "Уверенность",
    "Правило поиска",
    "Лист проекта",
    "Тип листа",
    "PDF",
    "Стр.",
    "Фрагмент короткий",
    "Комментарий parser-а",
    "evidence_id",
    "candidate_id",
]

EXPECTED_06_BLOCKS = {
    "Блок 0: Summary запуска": ["Показатель", "Значение", "Комментарий"],
    "Блок 1: logical sheets": [
        "source_pdf",
        "page",
        "drawing_sheet_number",
        "logical_sheet_title",
        "logical_sheet_type",
        "section_hint",
        "confidence",
        "matched_terms",
        "used_by_stage1",
        "comment",
    ],
    "Блок 2: extracted parameters raw": [
        "technical_key",
        "Параметр",
        "value_summary",
        "unit",
        "status",
        "confidence",
        "source_pdf",
        "page",
        "logical_sheet_title",
        "logical_sheet_type",
        "rule",
        "evidence_id",
        "candidate_id",
        "has_full_json",
        "has_raw_context",
        "comment",
    ],
    "Блок 3: evidence raw contexts": [
        "evidence_id",
        "source_pdf",
        "page",
        "logical_sheet_title",
        "logical_sheet_type",
        "short_fragment",
        "raw_context_full",
        "confidence",
        "used_by_keys",
    ],
    "Блок 4: full JSON values": [
        "technical_key",
        "Параметр",
        "value_summary",
        "full_json",
        "evidence_id",
        "candidate_id",
        "comment",
    ],
}


def find_row_by_title(sheet, title: str) -> int:
    for row in range(1, sheet.max_row + 1):
        if str(sheet.cell(row, 1).value or "") == title:
            return row
    return 0


def run_anti_cheat(job_dir: Path, source_root: Path) -> None:
    errors: list[str] = []
    warnings: list[str] = []

    for path in source_root.rglob("*.py"):
        if "data/jobs" in str(path):
            continue
        if path.name == "anti_cheat.py":
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_SOURCE_STRINGS:
            if forbidden in text:
                errors.append(f"{path}: forbidden production-flow reference `{forbidden}`")

    resolution_path = job_dir / "pricing" / "earthworks_price_resolution.json"
    if resolution_path.exists():
        resolution = json.loads(resolution_path.read_text(encoding="utf-8"))
        for row in resolution.get("resolved_components", []):
            if row["price"] == 0 and row["component_code"] != "sand_manual_moving_work":
                warnings.append(f"{row['component_code']}: zero price exists; verify it is intentional.")

    snapshot_path = job_dir / "pricing" / "price_registry_snapshot.json"
    if not snapshot_path.exists():
        errors.append("price_registry_snapshot.json is missing.")

    workbook_path = job_dir / "google" / "review_workbook.xlsx"
    if workbook_path.exists():
        wb = load_workbook(workbook_path, read_only=False, data_only=False)
        expected_sheets = [
            "00_Конструктор сметы",
            "01_Проверка проекта",
            "02_Цены себестоимости",
            "03_Детали объемов",
            "04_Инструкция",
            "05_Кандидаты parser",
            "06_Сырые данные parser",
        ]
        if wb.sheetnames != expected_sheets:
            errors.append(f"Unexpected sheet order: {wb.sheetnames}")
        for ws in wb.worksheets:
            if ws.sheet_state != "visible":
                errors.append(f"{ws.title}: sheet must be visible.")
        ws = wb["01_Проверка проекта"]
        user_unit_values = [str(ws.cell(row, 3).value or "") for row in range(5, ws.max_row + 1)]
        if "routes" in user_unit_values or "items" in user_unit_values:
            errors.append("01_Проверка проекта contains routes/items as user-facing units.")
        user_statuses = [str(ws.cell(row, 4).value or "") for row in range(5, ws.max_row + 1)]
        forbidden_statuses = {"found", "found_needs_review", "auto_calculated", "manual_required", "ambiguous", "📋 См. детали", "🟦 Рассчитано"}
        if any(status in forbidden_statuses for status in user_statuses):
            errors.append("01_Проверка проекта contains technical English statuses.")
        summary_values = [str(ws.cell(2, col).value or "").strip() for col in range(1, 5)]
        required_summary_prefixes = ["Найдено уверенно:", "Проверьте:", "Не найдено:", "Ручной ввод:"]
        for i, prefix in enumerate(required_summary_prefixes):
            if i < len(summary_values) and not summary_values[i].startswith(prefix):
                errors.append(f"01_Проверка проекта summary cell {i+1} must start with `{prefix}`, got `{summary_values[i] if i < len(summary_values) else ''}`")
        for row in range(5, ws.max_row + 1):
            for col in range(1, 10):
                value = str(ws.cell(row, col).value or "")
                if value.strip().startswith("{") or value.strip().startswith("["):
                    errors.append("01_Проверка проекта contains JSON in user-facing columns.")
                    break
        header_map = {str(ws.cell(4, col).value or ""): col for col in range(1, ws.max_column + 1)}
        rows_by_key = {}
        for row in range(5, ws.max_row + 1):
            technical_key = str(ws.cell(row, header_map.get("technical_key", 10)).value or "")
            if technical_key:
                rows_by_key[technical_key] = row
        if rows_by_key:
            detail_keys = ["trench_routes", "trench_volume_m3", "communications_pipe_items"]
            for technical_key in detail_keys:
                row = rows_by_key.get(technical_key)
                if not row:
                    errors.append(f"{technical_key}: row is missing from 01_Проверка проекта.")
                    continue
                extraction_status = str(ws.cell(row, header_map.get("extraction_status", 11)).value or "")
                if extraction_status == "found":
                    if str(ws.cell(row, header_map.get("Статус", 4)).value or "") != "🟧 Проверьте":
                        errors.append(f"{technical_key}: must use 🟧 Проверьте when found.")
                    if str(ws.cell(row, header_map.get("Фрагмент проекта", 7)).value or "") != "См. лист 03_Детали объемов.":
                        errors.append(f"{technical_key}: must point fragment to 03_Детали объемов when found.")
                    if str(ws.cell(row, header_map.get("confidence", 12)).value or "") not in ("high", "medium"):
                        errors.append(f"{technical_key}: must have high or medium confidence when found.")
                    if technical_key == "communications_pipe_items":
                        src_val = str(ws.cell(row, header_map.get("Источник", 6)).value or "")
                        if not any(t in src_val for t in VALID_COMMUNICATION_SCHEME_TITLES):
                            errors.append("communications_pipe_items must source from a valid communication scheme when found.")

            comm_len_row = rows_by_key.get("communications_length_m")
            if comm_len_row:
                comm_extraction_status = str(ws.cell(comm_len_row, header_map.get("extraction_status", 11)).value or "")
                if comm_extraction_status in ("auto_calculated", "found"):
                    if str(ws.cell(comm_len_row, header_map.get("Источник", 6)).value or "") != "Рассчитано из труб коммуникаций":
                        errors.append("communications_length_m must source from pipes when calculated.")

        ws05 = wb["05_Кандидаты parser"]
        actual_05_headers = [ws05.cell(2, col).value for col in range(1, len(EXPECTED_05_HEADERS) + 1)]
        if actual_05_headers != EXPECTED_05_HEADERS:
            errors.append(f"05_Кандидаты parser has wrong headers: {actual_05_headers}")
        title_text = str(ws05.cell(1, 1).value or "")
        if "Полный JSON и raw OCR находятся на листе 06" not in title_text:
            errors.append("05_Кандидаты parser title must point raw JSON/OCR to sheet 06.")
        candidate_rows = {}
        for row in range(3, ws05.max_row + 1):
            technical_key = str(ws05.cell(row, 2).value or "").strip()
            if technical_key:
                candidate_rows[technical_key] = row
            value_summary = str(ws05.cell(row, 3).value or "").strip()
            if value_summary.startswith(("[", "{")):
                errors.append("05_Кандидаты parser contains JSON in `Значение кратко`.")
                break
            fragment = str(ws05.cell(row, 12).value or "")
            if len(fragment) > 250:
                errors.append("05_Кандидаты parser contains an overlong fragment.")
                break
        spec_05_required = {
            "trench_routes": {"rule": "trench_table_routes"},
            "communications_pipe_items": {"rule": "pipe_items_from_spec_rows"},
            "communications_length_m": {"rule": "calculated_from_pipe_items"},
            "geotextile_laying_area_m2": {"status": "допущение", "confidence": "medium", "rule": "poc_assumption_equal_to_geotextile_area"},
        }
        for technical_key, expectation in spec_05_required.items():
            row = candidate_rows.get(technical_key)
            if not row:
                errors.append(f"05_Кандидаты parser: missing row for `{technical_key}`.")
                continue
            if "status" in expectation and str(ws05.cell(row, 5).value or "") != expectation["status"]:
                errors.append(f"05_Кандидаты parser: `{technical_key}` has unexpected status.")
            if "confidence" in expectation and str(ws05.cell(row, 6).value or "") != expectation["confidence"]:
                errors.append(f"05_Кандидаты parser: `{technical_key}` has unexpected confidence.")
            if "rule" in expectation and str(ws05.cell(row, 7).value or "") != expectation["rule"]:
                errors.append(f"05_Кандидаты parser: `{technical_key}` has unexpected rule.")
            if technical_key == "trench_routes" and str(ws05.cell(row, 5).value or "") == "выбран":
                if "Таблица траншей" not in str(ws05.cell(row, 12).value or ""):
                    errors.append("05_Кандидаты parser: `trench_routes` fragment must mention `Таблица траншей` when found.")
            if technical_key == "communications_pipe_items" and str(ws05.cell(row, 9).value or ""):
                if str(ws05.cell(row, 8).value or "") not in VALID_COMMUNICATION_SCHEME_TITLES:
                    errors.append("05_Кандидаты parser: `communications_pipe_items` must source from a valid communication scheme when found.")
                if str(ws05.cell(row, 9).value or "") != "communications_scheme":
                    errors.append("05_Кандидаты parser: `communications_pipe_items` must use `communications_scheme` when found.")

        ws06 = wb["06_Сырые данные parser"]
        for title, headers in EXPECTED_06_BLOCKS.items():
            row = find_row_by_title(ws06, title)
            if not row:
                errors.append(f"06_Сырые данные parser is missing block title `{title}`.")
                continue
            actual_headers = [ws06.cell(row + 1, col).value for col in range(1, len(headers) + 1)]
            if actual_headers != headers:
                errors.append(f"06_Сырые данные parser block `{title}` has wrong headers: {actual_headers}")

        summary_row = find_row_by_title(ws06, "Блок 0: Summary запуска")
        if summary_row:
            summary_map = {}
            for row in range(summary_row + 2, ws06.max_row + 1):
                key = str(ws06.cell(row, 1).value or "").strip()
                if not key:
                    continue
                if key.startswith("Блок "):
                    break
                summary_map[key] = str(ws06.cell(row, 2).value or "")
            for required_key in [
                "job_id",
                "created_at",
                "pages_count",
                "tables_count",
                "logical_sheets_count",
                "candidates_count",
                "found_count",
                "attention_count",
                "missing_count",
                "stage1_summary_path",
                "parser_report_path",
            ]:
                if required_key not in summary_map:
                    errors.append(f"06_Сырые данные parser summary is missing `{required_key}`.")
            for path_key in ["stage1_summary_path", "parser_report_path"]:
                if summary_map.get(path_key) and not Path(summary_map[path_key]).exists():
                    errors.append(f"06_Сырые данные parser summary path does not exist: {summary_map[path_key]}")

        extracted_row = find_row_by_title(ws06, "Блок 2: extracted parameters raw")
        if extracted_row:
            block2_headers = [ws06.cell(extracted_row + 1, col).value for col in range(1, len(EXPECTED_06_BLOCKS["Блок 2: extracted parameters raw"]) + 1)]
            if block2_headers != EXPECTED_06_BLOCKS["Блок 2: extracted parameters raw"]:
                errors.append(f"06_Сырые данные parser block `Блок 2: extracted parameters raw` has wrong headers: {block2_headers}")
            block2_map = {str(header or ""): idx for idx, header in enumerate(block2_headers, start=1)}
            raw_rows_by_key = {}
            for row in range(extracted_row + 2, ws06.max_row + 1):
                key = str(ws06.cell(row, 1).value or "").strip()
                if not key:
                    continue
                if key.startswith("Блок "):
                    break
                raw_rows_by_key[key] = row
                value_summary = str(ws06.cell(row, block2_map.get("value_summary", 3)).value or "").strip()
                if value_summary.startswith(("[", "{")):
                    errors.append(f"06_Сырые данные parser: `{key}` value_summary must be short.")
                    break
            expected_rules = {
                "pit_area_m2": "area_line_by_terms_and_unit",
                "trench_routes": "trench_table_routes",
                "communications_pipe_items": "pipe_items_from_spec_rows",
                "communications_length_m": "calculated_from_pipe_items",
            }
            for technical_key, expected_rule in expected_rules.items():
                row = raw_rows_by_key.get(technical_key)
                if not row:
                    errors.append(f"06_Сырые данные parser: missing extracted row for `{technical_key}`.")
                    continue
                actual_rule = str(ws06.cell(row, block2_map.get("rule", 0)).value or "") if block2_map.get("rule", 0) else ""
                if actual_rule != expected_rule:
                    errors.append(f"06_Сырые данные parser: `{technical_key}` has wrong `rule` value `{actual_rule}`; expected `{expected_rule}`.")

        json_row = find_row_by_title(ws06, "Блок 4: full JSON values")
        if json_row:
            json_keys = set()
            for row in range(json_row + 2, ws06.max_row + 1):
                key = str(ws06.cell(row, 1).value or "").strip()
                if not key:
                    continue
                if key.startswith("Блок "):
                    break
                json_keys.add(key)
            for required_key in ["trench_routes", "communications_pipe_items"]:
                if required_key not in json_keys:
                    errors.append(f"06_Сырые данные parser JSON block missing `{required_key}`.")
        details_ws = wb["03_Детали объемов"]
        expected_detail_headers = [
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
        ]
        actual_detail_headers = [details_ws.cell(1, col).value for col in range(1, 15)]
        if actual_detail_headers != expected_detail_headers:
            errors.append(f"03_Детали объемов has wrong headers: {actual_detail_headers}")
        forbidden_detail_headers = {
            "Исправить / ввести",
            "Исправить длину",
            "Исправить глубину",
            "Исправить ширину",
            "Исправить объём",
            "Исправить итоговую длину",
        }
        actual_detail_header_set = {str(details_ws.cell(1, col).value or "") for col in range(1, details_ws.max_column + 1)}
        forbidden_detail_present = sorted(forbidden_detail_headers & actual_detail_header_set)
        if forbidden_detail_present:
            errors.append(f"03_Детали объемов contains forbidden headers: {forbidden_detail_present}")

        detail_rows = [
            [details_ws.cell(row, col).value for col in range(1, 15)]
            for row in range(2, details_ws.max_row + 1)
        ]
        if not any(str(row[0] or "") == "Траншеи" for row in detail_rows):
            errors.append("03_Детали объемов must contain the `Траншеи` section row.")
        if not any(str(row[0] or "") == "Коммуникации" for row in detail_rows):
            errors.append("03_Детали объемов must contain the `Коммуникации` section row.")

        communication_rows = [row for row in detail_rows if str(row[0] or "") == "Коммуникация"]
        for row in communication_rows:
            name = str(row[1] or "")
            included = str(row[10] or "")
            source = str(row[11] or "")
            if source and not any(t in source for t in VALID_COMMUNICATION_SCHEME_TITLES):
                errors.append(f"{name}: communication source must mention a valid communication scheme.")
            if included and included != "да":
                errors.append(f"{name}: communication `Включено` must be `да`, got {included}")

        for row in detail_rows:
            row_type = str(row[0] or "")
            if row_type == "Траншея":
                fragment = str(row[12] or "")
                if fragment and not fragment.startswith("Таблица траншей: "):
                    errors.append(f"{row[1]}: trench fragment must be a short `Таблица траншей:` note.")
                if "\n" in fragment:
                    errors.append(f"{row[1]}: trench fragment must not contain raw OCR line breaks.")
                if str(row[13] or "").strip():
                    errors.append(f"{row[1]}: `Комментарий Елены` must be empty.")

        instruction_ws = wb["04_Инструкция"]
        instruction_text = "\n".join(
            str(instruction_ws.cell(row, col).value or "")
            for row in range(1, instruction_ws.max_row + 1)
            for col in range(1, instruction_ws.max_column + 1)
        )
        for forbidden in ["См. детали", "Строки “См. детали”"]:
            if forbidden in instruction_text:
                errors.append(f"04_Инструкция contains forbidden text `{forbidden}`.")
        required_instruction_texts = [
            "Где именно проверять оранжевую строку, написано в колонке “Что нужно сделать”.",
            "Лист 03_Детали объемов — справочный, не источник ручных правок.",
        ]
        for required in required_instruction_texts:
            if required not in instruction_text:
                errors.append(f"04_Инструкция is missing required text `{required}`.")
        price_ws = wb["02_Цены себестоимости"]
        expected_price_headers = [
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
            "calc_price_key",
            "price_registry_code",
            "fallback_key",
            "selected_price_source",
        ]
        actual_price_headers = [price_ws.cell(1, col).value for col in range(1, len(expected_price_headers) + 1)]
        if actual_price_headers != expected_price_headers:
            errors.append(f"02_Цены себестоимости has wrong headers: {actual_price_headers}")
        forbidden_price_headers = {
            "Цена материалов / машин / механизмов",
            "Цена работ",
            "Источник цены материалов",
            "Источник цены работ",
        }
        all_price_headers = {str(price_ws.cell(1, col).value or "") for col in range(1, price_ws.max_column + 1)}
        forbidden_present = sorted(forbidden_price_headers & all_price_headers)
        if forbidden_present:
            errors.append(f"02_Цены себестоимости contains forbidden headers: {forbidden_present}")
        price_rows = [
            [price_ws.cell(row, col).value for col in range(1, min(price_ws.max_column, len(expected_price_headers)) + 1)]
            for row in range(2, price_ws.max_row + 1)
        ]
        flat_text = "\n".join("\t".join(str(value or "") for value in row) for row in price_rows)
        if "явный 0 / не применяется" in flat_text:
            errors.append("02_Цены себестоимости contains forbidden text `явный 0 / не применяется`.")
        excavator_kinds = [row[1] for row in price_rows if row[0] == "Экскаватор JCB"]
        if excavator_kinds != ["Аренда/механизм", "Работа оператора/бригады"]:
            errors.append(f"Экскаватор JCB must be two flat rows; got {excavator_kinds}")
        forbidden_artificial_pairs = {
            ("Геотекстиль Дорнит 300 г.м2", "Работа"),
            ("Укладка геотекстиля", "Материал"),
            ("Песок строительный", "Работа"),
        }
        actual_pairs = {(row[0], row[1]) for row in price_rows}
        bad_pairs = sorted(forbidden_artificial_pairs & actual_pairs)
        if bad_pairs:
            errors.append(f"02_Цены себестоимости contains artificial zero pairs: {bad_pairs}")
        allowed_price_sources = {"price_registry", "fallback"}
        registry_warning_emitted = False
        for row in price_rows:
            line_name = str(row[0] or "")
            calculation_price = row[5]
            source = str(row[7] or "").strip()
            needs_attention = str(row[8] or "").strip().lower()
            calc_price_key = str(row[10] or "").strip()
            price_registry_code = str(row[11] or "").strip()
            fallback_key = str(row[12] or "").strip()
            selected_price_source = str(row[13] or "").strip()
            if not source:
                errors.append(f"{line_name}: price source must be filled.")
            if calculation_price in (None, "") and needs_attention != "да":
                errors.append(f"{line_name}: calculation price must be filled unless attention is required.")
            if not calc_price_key:
                errors.append(f"{line_name}: calc_price_key must be filled.")
            if selected_price_source not in allowed_price_sources:
                errors.append(f"{line_name}: selected_price_source must be price_registry or fallback.")
            if selected_price_source == "fallback":
                if price_registry_code:
                    errors.append(f"{line_name}: fallback rows must not have price_registry_code.")
                if not fallback_key.startswith("fallback."):
                    errors.append(f"{line_name}: fallback rows must have fallback_key starting with `fallback.`.")
            if line_name == "Геотекстиль Дорнит 300 г.м2":
                if selected_price_source != "price_registry":
                    errors.append("Геотекстиль Дорнит 300 г.м2 must use price_registry as selected_price_source.")
                if not price_registry_code and not registry_warning_emitted:
                    warnings.append("warning: price_registry_code is not available from resolver yet")
                    registry_warning_emitted = True
            if line_name == "Расходные материалы":
                if calc_price_key != "consumables_amount":
                    errors.append("Расходные материалы must use calc_price_key consumables_amount.")
                if selected_price_source != "fallback":
                    errors.append("Расходные материалы must use fallback as selected_price_source.")
                if fallback_key != "fallback.consumables_amount":
                    errors.append("Расходные материалы must use fallback.consumables_amount as fallback_key.")
    else:
        errors.append("review_workbook.xlsx is missing.")

    report = {
        "status": "failed" if errors else "clean",
        "errors": errors,
        "warnings": warnings,
        "checks": [
            "Google price_registry read-only snapshot exists.",
            "Fallback from ЮСВ is only used by pricing resolver.",
            "No auto-publish scripts are referenced in production-flow.",
            "No visible artificial zero price components.",
            "Price sheet is a flat list of real price components.",
            "Price registry is used only by exact registry code.",
            "Visible technical sheets are present.",
            "First sheet does not expose routes/items/JSON/English technical statuses.",
            "01_Проверка проекта uses action-based statuses and technical confidence/extraction fields.",
            "03_Детали объемов uses the approved unified detail table without manual correction columns.",
            "05_Кандидаты parser uses short summaries instead of JSON dumps.",
            "06_Сырые данные parser keeps summary, raw contexts, and full JSON in separate blocks.",
        ],
    }
    out = job_dir / "reports" / "anti_cheat_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Anti-cheat Report", "", f"Status: `{report['status']}`", "", "## Errors"]
    lines.extend(f"- {error}" for error in errors)
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in warnings)
    lines.extend(["", "## Checks"])
    lines.extend(f"- {check}" for check in report["checks"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (job_dir / "reports" / "anti_cheat_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if errors:
        raise RuntimeError("Anti-cheat failed: " + "; ".join(errors))
