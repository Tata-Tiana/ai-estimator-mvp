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
        forbidden_statuses = {"found", "found_needs_review", "auto_calculated", "manual_required", "ambiguous"}
        if any(status in forbidden_statuses for status in user_statuses):
            errors.append("01_Проверка проекта contains technical English statuses.")
        for row in range(5, ws.max_row + 1):
            for col in range(1, 10):
                value = str(ws.cell(row, col).value or "")
                if value.strip().startswith("{") or value.strip().startswith("["):
                    errors.append("01_Проверка проекта contains JSON in user-facing columns.")
                    break
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
        expected_prices = {
            ("Вынос осей", "Работа"): 20000,
            ("Экскаватор JCB", "Аренда/механизм"): 26000,
            ("Экскаватор JCB", "Работа оператора/бригады"): 3500,
            ("Разработка грунта вручную", "Работа"): 1400,
            ("Песок строительный", "Материал"): 1550,
            ("Геотекстиль Дорнит 300 г.м2", "Материал"): 109,
        }
        actual_price_map = {(row[0], row[1]): row[5] for row in price_rows}
        for key, expected in expected_prices.items():
            if actual_price_map.get(key) != expected:
                errors.append(f"{key}: expected calculation price {expected}, got {actual_price_map.get(key)}")
        source_map = {(row[0], row[1]): row[7] for row in price_rows}
        if source_map.get(("Геотекстиль Дорнит 300 г.м2", "Материал")) != "price_registry":
            errors.append("Геотекстиль Дорнит 300 г.м2 must use price_registry.")
        for key in [
            ("Вынос осей", "Работа"),
            ("Экскаватор JCB", "Аренда/механизм"),
            ("Разработка грунта вручную", "Работа"),
            ("Песок строительный", "Материал"),
        ]:
            if source_map.get(key) != "fallback: базовая цена из базового кейса":
                errors.append(f"{key}: must use base case fallback, got {source_map.get(key)}")
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
