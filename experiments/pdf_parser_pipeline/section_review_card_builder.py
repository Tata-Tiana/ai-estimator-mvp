"""Build per-section review cards from parsed PDF artifacts."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from section_schema import REPO_ROOT, get_section_schema


SOURCE_PROJECT_DIR = REPO_ROOT / "experiments/pdf_tests/projects/usv_yusupovo_village"
MERGED_DIR = SOURCE_PROJECT_DIR / "merged"
PARSED_DIR = SOURCE_PROJECT_DIR / "parsed"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_case_inputs(case_dir: Path) -> list[str]:
    """Copy lightweight parser artifacts into the pipeline case if missing."""
    warnings: list[str] = []
    input_dir = case_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    for name in [
        "project_manifest.json",
        "extraction_report.md",
        "extracted_parameters_for_review.json",
        "project_full_text_by_sources.md",
    ]:
        source = MERGED_DIR / name
        target = input_dir / name
        if not target.exists():
            if source.exists():
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                warnings.append(f"Missing merged artifact: {source}")

    parsed_target_root = input_dir / "parsed"
    parsed_target_root.mkdir(exist_ok=True)
    for source_dir in sorted(PARSED_DIR.glob("*")):
        if not source_dir.is_dir():
            continue
        target_dir = parsed_target_root / source_dir.name
        target_dir.mkdir(parents=True, exist_ok=True)
        for artifact in ["full_text.txt", "pages_text.json", "blocks.json", "tables.json", "tables.xlsx", "summary.json"]:
            source = source_dir / artifact
            target = target_dir / artifact
            if not target.exists() and source.exists():
                shutil.copy2(source, target)
        # Page images are intentionally not duplicated in this case folder.
        # They remain available in experiments/pdf_tests/.../parsed/*/page_images.
    return warnings


def load_manifest(case_dir: Path) -> dict[str, Any]:
    return read_json(case_dir / "input/project_manifest.json", {})


def source_file_by_id(manifest: dict[str, Any]) -> dict[str, str]:
    return {source.get("source_id"): source.get("source_file", "") for source in manifest.get("sources", [])}


def load_pages(case_dir: Path) -> dict[str, dict[int, str]]:
    pages: dict[str, dict[int, str]] = {}
    parsed_root = case_dir / "input/parsed"
    for source_dir in parsed_root.iterdir() if parsed_root.exists() else []:
        pages_text = read_json(source_dir / "pages_text.json", [])
        source_pages: dict[int, str] = {}
        for item in pages_text:
            try:
                source_pages[int(item.get("page"))] = item.get("text", "")
            except (TypeError, ValueError):
                continue
        pages[source_dir.name] = source_pages
    return pages


def normalize_number(value: str) -> int | float | str:
    value = value.strip().replace("\u00a0", " ")
    numeric = value.replace(" ", "")
    if re.fullmatch(r"-?\d+", numeric):
        return int(numeric)
    if re.fullmatch(r"-?\d+[,.]\d+", numeric):
        return float(numeric.replace(",", "."))
    return re.sub(r"\s+", " ", value).strip()


def source_text_snippet(text: str, start: int, end: int, radius: int = 90) -> str:
    snippet = text[max(0, start - radius): min(len(text), end + radius)]
    return re.sub(r"\s+", " ", snippet).strip()


def page_title(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if any(token in line.lower() for token in ("план", "спецификация", "сечение", "разрез", "пояснительная", "узлы")):
            return line[:120]
    return lines[0][:120] if lines else ""


def search_parameter(parameter: dict[str, Any], section: dict[str, Any], pages: dict[str, dict[int, str]], source_files: dict[str, str]) -> dict[str, Any] | None:
    patterns = parameter.get("regex_patterns") or []
    if not patterns:
        return None

    for source_hint in section.get("source_hints", []):
        source_id = source_hint["source_id"]
        selected_pages = source_hint.get("pages") or sorted(pages.get(source_id, {}).keys())
        for page in selected_pages:
            text = pages.get(source_id, {}).get(page, "")
            if not text:
                continue
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
                if not match:
                    continue
                raw_value = match.groupdict().get("value") or match.groupdict().get("value2") or match.group(1)
                return {
                    "value": normalize_number(str(raw_value)),
                    "source_file": source_files.get(source_id, ""),
                    "source_id": source_id,
                    "page": page,
                    "section_title": page_title(text),
                    "source_text": source_text_snippet(text, match.start(), match.end()),
                }
    return None


def build_parameter_entry(parameter: dict[str, Any], section: dict[str, Any], pages: dict[str, dict[int, str]], source_files: dict[str, str]) -> dict[str, Any]:
    found = search_parameter(parameter, section, pages, source_files)
    input_type = parameter["input_type"]
    if found:
        review_status = "control_only" if input_type == "control_only" else "needs_human_review"
        confidence = "extracted_from_specification" if input_type != "control_only" else "control_only"
        value = found["value"]
    else:
        value = None
        if input_type == "control_only":
            review_status = "control_only"
            confidence = "control_only"
        elif input_type == "manual":
            review_status = "manual_required"
            confidence = "manual_required"
        elif parameter.get("required"):
            review_status = "missing"
            confidence = "not_found"
        else:
            review_status = "manual_required" if input_type in {"price", "default", "calculation_constant"} else "missing"
            confidence = "not_found"

    entry = {
        "parameter_code": parameter["parameter_code"],
        "calculator_input_key": parameter["calculator_input_key"],
        "label": parameter["label"],
        "value": value,
        "unit": parameter.get("unit", ""),
        "source_file": (found or {}).get("source_file", ""),
        "source_id": (found or {}).get("source_id", ""),
        "page": (found or {}).get("page", ""),
        "section_title": (found or {}).get("section_title", ""),
        "source_text": (found or {}).get("source_text", ""),
        "review_status": review_status,
        "confidence": confidence,
    }
    return entry


def render_review_card_md(card: dict[str, Any]) -> str:
    found = [p for p in card["parameters"] if p["value"] not in (None, "")]
    missing = [p for p in card["parameters"] if p["review_status"] in {"missing", "manual_required"}]
    calc = [p for p in card["parameters"] if p["review_status"] != "control_only"]
    lines = [
        f"# Review card: {card['section_name']}",
        "",
        "## Что система нашла",
        "| parameter_code | value | unit | source | page | status |",
        "|---|---:|---|---|---:|---|",
    ]
    for item in found:
        lines.append(f"| {item['parameter_code']} | {item['value']} | {item['unit']} | {item['source_file']} | {item['page']} | {item['review_status']} |")
    if not found:
        lines.append("| - | - | - | - | - | - |")

    lines.extend([
        "",
        "## Что проверить Елене",
    ])
    for question in card["review_questions_for_elena"]:
        lines.append(f"- {question}")
    if not card["review_questions_for_elena"]:
        lines.append("- Проверить параметры со статусами needs_human_review, manual_required и missing.")

    lines.extend([
        "",
        "## Параметры для калькулятора",
        "| parameter_code | calculator_input_key | status |",
        "|---|---|---|",
    ])
    for item in calc:
        lines.append(f"| {item['parameter_code']} | {item['calculator_input_key']} | {item['review_status']} |")

    lines.extend([
        "",
        "## Missing / manual_required",
        "| parameter_code | label | status |",
        "|---|---|---|",
    ])
    for item in missing:
        lines.append(f"| {item['parameter_code']} | {item['label']} | {item['review_status']} |")
    if not missing:
        lines.append("| - | - | - |")
    lines.append("")
    return "\n".join(lines)


def review_questions_for_section(section_code: str) -> list[str]:
    base = {
        "earthworks": [
            "Подтвердить, какие объемы земляных работ являются проектными, а какие ручными расчетами сметы.",
        ],
        "foundation_slab": [
            "Подтвердить, что бетон 81 м3 относится к нужному объему для калькулятора фундаментной плиты.",
            "Подтвердить трактовку ЭППС 150 мм термовставок.",
            "Подтвердить, использовать ли PLANTER 320 м2 из спецификации или геометрическую площадь как контроль.",
        ],
        "waterproofing": [
            "Подтвердить периметр/высоту гидроизоляции, если они не берутся надежно из PDF.",
        ],
        "load_bearing_walls_lintels": [
            "Подтвердить объемы газобетона и веса арматуры по спецификации КР-2.",
        ],
        "floor_slab_1": [
            "Проверить балки Б-1/Б-2/Б-3 и ручные геометрические параметры.",
        ],
        "floor_slab_2": [
            "Подтвердить, что объем бетонирования 16,5 м3 остается проектным/manual input.",
        ],
        "flat_roof": [
            "Проверить площади кровли и ручные объемы уклонных плит от поставщика.",
        ],
        "schiedel_vent_channels": [
            "Подтвердить количества Schiedel 24 шт и 8 шт по спецификации/таблице Елены.",
            "Подтвердить ручную доставку вентканалов.",
        ],
    }
    return base.get(section_code, ["Проверить найденные и отсутствующие параметры раздела."])


def build_review_cards(case_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    warnings = ensure_case_inputs(case_dir)
    manifest = load_manifest(case_dir)
    project = manifest.get("project", "usv_yusupovo_village")
    pages = load_pages(case_dir)
    source_files = source_file_by_id(manifest)
    sections = get_section_schema(REPO_ROOT)

    cards: list[dict[str, Any]] = []
    review_cards_dir = case_dir / "review_cards"
    review_cards_dir.mkdir(parents=True, exist_ok=True)

    for section in sections:
        parameters = [build_parameter_entry(parameter, section, pages, source_files) for parameter in section["parameters"]]
        priority_pages = []
        for hint in section.get("source_hints", []):
            for page in hint.get("pages", []):
                text = pages.get(hint["source_id"], {}).get(page, "")
                priority_pages.append({
                    "source_id": hint["source_id"],
                    "source_file": source_files.get(hint["source_id"], ""),
                    "page": page,
                    "title": page_title(text) or (hint.get("titles") or [""])[0],
                })

        card = {
            "project": project,
            "section": section["section_code"],
            "section_name": section["section_name"],
            "source_scope": {
                "source_files": sorted({source_files.get(h["source_id"], "") for h in section.get("source_hints", [])}),
                "priority_pages": priority_pages,
            },
            "review_status": "needs_human_review",
            "parameters": parameters,
            "calculator_mapping": {p["parameter_code"]: p["calculator_input_key"] for p in parameters},
            "review_questions_for_elena": review_questions_for_section(section["section_code"]),
        }
        write_json(review_cards_dir / f"{section['section_code']}_review_card.json", card)
        (review_cards_dir / f"{section['section_code']}_review_card.md").write_text(render_review_card_md(card), encoding="utf-8")
        cards.append(card)

    return cards, warnings
