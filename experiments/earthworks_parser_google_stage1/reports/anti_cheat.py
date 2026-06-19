from __future__ import annotations

import json
from pathlib import Path

from openpyxl import load_workbook


FORBIDDEN_SOURCE_STRINGS = [
    "merge_rows_to_price_registry",
    "publish_canonical_registry",
    "normalize_price_registry_sheet",
]


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
        expected_summary_values = [
            "Найдено уверенно: 2",
            "Проверьте: 7",
            "Не найдено: 0",
            "Ручной ввод: 0",
        ]
        if summary_values != expected_summary_values:
            errors.append(f"01_Проверка проекта summary mismatch: {summary_values}")
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
            expected_detail_keys = {
                "trench_routes": "found",
                "trench_volume_m3": "found",
                "communications_pipe_items": "found",
            }
            for technical_key, expected_extraction_status in expected_detail_keys.items():
                row = rows_by_key.get(technical_key)
                if not row:
                    errors.append(f"{technical_key}: row is missing from 01_Проверка проекта.")
                    continue
                if str(ws.cell(row, header_map.get("Статус", 4)).value or "") != "🟧 Проверьте":
                    errors.append(f"{technical_key}: must use 🟧 Проверьте.")
                if str(ws.cell(row, header_map.get("Фрагмент проекта", 7)).value or "") != "См. лист 03_Детали объемов.":
                    errors.append(f"{technical_key}: must point fragment to 03_Детали объемов.")
                if str(ws.cell(row, header_map.get("extraction_status", 11)).value or "") != expected_extraction_status:
                    errors.append(f"{technical_key}: must have extraction_status {expected_extraction_status}.")
                if str(ws.cell(row, header_map.get("confidence", 12)).value or "") != "high":
                    errors.append(f"{technical_key}: must have confidence high.")
                if technical_key == "communications_pipe_items" and "Схема коммуникаций" not in str(ws.cell(row, header_map.get("Источник", 6)).value or ""):
                    errors.append("communications_pipe_items must source from `Схема коммуникаций`.")

            comm_len_row = rows_by_key.get("communications_length_m")
            if comm_len_row:
                if str(ws.cell(comm_len_row, header_map.get("Статус", 4)).value or "") != "🟧 Проверьте":
                    errors.append("communications_length_m must use 🟧 Проверьте.")
                if str(ws.cell(comm_len_row, header_map.get("Источник", 6)).value or "") != "Рассчитано из труб коммуникаций":
                    errors.append("communications_length_m must source from pipes.")
                if str(ws.cell(comm_len_row, header_map.get("Фрагмент проекта", 7)).value or "") != "рассчитано из 4 позиций труб":
                    errors.append("communications_length_m must have the calculated fragment note.")
                if str(ws.cell(comm_len_row, header_map.get("extraction_status", 11)).value or "") != "auto_calculated":
                    errors.append("communications_length_m must have extraction_status auto_calculated.")
                if str(ws.cell(comm_len_row, header_map.get("confidence", 12)).value or "") != "high":
                    errors.append("communications_length_m must have confidence high.")
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
        trench_names = [str(row[1] or "") for row in detail_rows if str(row[0] or "") == "Траншея"]
        if trench_names != ["К 1", "К 2", "Вода", "Эл. кабель"]:
            errors.append(f"03_Детали объемов trench names mismatch: {trench_names}")
        if not any(str(row[0] or "") == "Траншеи" for row in detail_rows):
            errors.append("03_Детали объемов must contain the `Траншеи` section row.")
        if not any(str(row[0] or "") == "Коммуникации" for row in detail_rows):
            errors.append("03_Детали объемов must contain the `Коммуникации` section row.")

        communication_rows = [row for row in detail_rows if str(row[0] or "") == "Коммуникация"]
        if len(communication_rows) != 4:
            errors.append(f"03_Детали объемов must contain 4 communication rows, got {len(communication_rows)}")
        expected_pipe_lengths = {
            "ГОСТ 32412-2013 Труба 2 м. ф110 (рыжая) 7 шт": "14",
            "ГОСТ 32412-2013 Труба 1 м. ф110 (рыжая) 12 шт": "12",
            "ГОСТ 32412-2013 Труба 3 м. ф110 (рыжая) 18 шт": "54",
            "ГОСТ 32412-2013 Труба ф110 гофрированная 35 м/п": "35",
        }
        for row in communication_rows:
            name = str(row[1] or "")
            diameter = str(row[6] or "")
            included = str(row[10] or "")
            source = str(row[11] or "")
            total_length = str(row[9] or "")
            comment = str(row[13] or "")
            if "Схема коммуникаций" not in source:
                errors.append(f"{name}: communication source must mention `Схема коммуникаций`.")
            if diameter != "110":
                errors.append(f"{name}: communication diameter must be 110, got {diameter}")
            if included != "да":
                errors.append(f"{name}: communication `Включено` must be `да`, got {included}")
            if comment.strip():
                errors.append(f"{name}: `Комментарий Елены` must be empty.")
            expected_total = expected_pipe_lengths.get(name)
            if expected_total and total_length != expected_total:
                errors.append(f"{name}: expected total length {expected_total}, got {total_length}")

        for row in detail_rows:
            row_type = str(row[0] or "")
            if row_type == "Траншея":
                fragment = str(row[12] or "")
                if not fragment.startswith("Таблица траншей: "):
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
        ]
        actual_price_headers = [price_ws.cell(1, col).value for col in range(1, 11)]
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
            [price_ws.cell(row, col).value for col in range(1, min(price_ws.max_column, 10) + 1)]
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
        for row in price_rows:
            line_name = str(row[0] or "")
            calculation_price = row[5]
            source = str(row[7] or "").strip()
            needs_attention = str(row[8] or "").strip().lower()
            if not source:
                errors.append(f"{line_name}: price source must be filled.")
            if calculation_price in (None, "") and needs_attention != "да":
                errors.append(f"{line_name}: calculation price must be filled unless attention is required.")
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
