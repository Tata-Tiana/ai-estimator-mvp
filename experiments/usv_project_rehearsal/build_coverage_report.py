from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAPPED_PATH = DATA_DIR / "mapped_parameters.json"
COVERAGE_REPORT_PATH = DATA_DIR / "coverage_report.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def bullet_rows(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["- Нет."]
    return [
        f"- {row['section_name']} :: `{row['calculator_input_key']}` — {row['label']}"
        + (f" = {row.get('value_from_pdf')} {row.get('unit')}" if row.get("value_from_pdf") not in (None, "") else "")
        + (f" ({row.get('source_pdf')} p.{row.get('page')})" if row.get("source_pdf") else "")
        for row in rows
    ]


def build_coverage_report() -> Path:
    mapped = load_json(MAPPED_PATH)
    relevant = [row for row in mapped if row.get("required_status") in {"AUTO_PROJECT", "SUPPLIER_INPUT", "MANUAL_REQUIRED", "OPTIONAL_CONTROL"}]
    counts = Counter(row["found_status"] for row in relevant)
    auto_project = [row for row in relevant if row.get("required_status") == "AUTO_PROJECT"]
    section_counts: dict[str, Counter] = defaultdict(Counter)
    for row in relevant:
        section_counts[row["section_name"]][row["found_status"]] += 1
        section_counts[row["section_name"]]["total"] += 1

    found = [row for row in auto_project if row.get("found_status") == "found"]
    missing = [row for row in relevant if row.get("found_status") == "missing"]
    low = [row for row in relevant if row.get("found_status") == "low_confidence"]
    conflicts = [row for row in relevant if row.get("found_status") == "conflict"]
    suppliers = [row for row in relevant if row.get("found_status") == "supplier_required"]
    manual = [row for row in relevant if row.get("found_status") == "manual_required"]
    elena = [row for row in relevant if row.get("needs_elena_review")]

    lines = [
        "# Coverage Report: USV Project Rehearsal",
        "",
        "Это репетиция production-пайплайна по новым PDF ЮСВ. Калькуляторы и locked-кейсы не изменяются.",
        "",
        "## Общая статистика",
        "",
        f"- Всего production-relevant параметров: {len(relevant)}",
        f"- AUTO_PROJECT всего: {len(auto_project)}",
        f"- AUTO_PROJECT найдено: {len(found)}",
        f"- missing AUTO_PROJECT/controls: {len(missing)}",
        f"- low_confidence: {len(low)}",
        f"- conflicts: {len(conflicts)}",
        f"- SUPPLIER_INPUT: {len(suppliers)}",
        f"- MANUAL_REQUIRED: {len(manual)}",
        f"- Требуют review Елены/команды: {len(elena)}",
        "",
        "### По found_status",
        "",
    ]
    for status, count in counts.most_common():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Статистика по разделам", "", "| section | total | found | missing | low_confidence | supplier_required | manual_required |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for section, counter in section_counts.items():
        lines.append(
            f"| {section} | {counter['total']} | {counter['found']} | {counter['missing']} | "
            f"{counter['low_confidence']} | {counter['supplier_required']} | {counter['manual_required']} |"
        )

    lines.extend(["", "## Что проектировщик сделал хорошо", ""])
    lines.extend(bullet_rows(found[:80]))

    lines.extend(["", "## Чего не хватает", ""])
    lines.extend(bullet_rows(missing))

    lines.extend(["", "## Low Confidence / проверить единицы и контекст", ""])
    lines.extend(bullet_rows(low))

    lines.extend(["", "## Conflicts", ""])
    lines.extend(bullet_rows(conflicts))

    lines.extend(["", "## Что осталось Елене / поставщику", "", "### SUPPLIER_INPUT", ""])
    lines.extend(bullet_rows(suppliers))
    lines.extend(["", "### MANUAL_REQUIRED", ""])
    lines.extend(bullet_rows(manual))
    lines.extend(["", "### Missing / Low Confidence", ""])
    lines.extend(bullet_rows(missing + low + conflicts))

    lines.extend(
        [
            "",
            "## Рекомендации проектировщику",
            "",
            "- В спецификациях явно писать единицы измерения для арматуры: `м.п.` или `кг`, без неоднозначных таблиц.",
            "- Для плит перекрытий явно разделять: бетон плиты, бетон балок, площадь опалубки под плиту, торцевую опалубку и опалубку балок.",
            "- Для кровли отдельно указывать площади уровней и длины примыканий к парапетам/стенам.",
            "- Для уклонных плит кровли прикладывать раскладку/коммерческое предложение поставщика.",
            "- Для вентканалов явно указывать объем газоблока обкладки и общую длину кладки.",
            "",
        ]
    )

    COVERAGE_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return COVERAGE_REPORT_PATH


def main() -> int:
    path = build_coverage_report()
    print(f"coverage_report: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
