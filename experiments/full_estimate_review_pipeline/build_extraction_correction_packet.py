"""Build a universal second-pass correction packet from an extraction JSON.

This is deliberately not a project-specific validator. Its job is to collect places where the
first extraction likely saw useful project facts but did not place them into a clean calculator
field: needs_review rows, candidates, missing targets, numeric notes/raw text attached to null
values, and raw rows with unresolved mapping.

The output is meant to be sent back to the same GPT/Claude chat together with the original JSON
and PDFs, using prompts/extraction_second_pass_correction_prompt.md.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


NUMBER_RE = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?(?:\s*[+]\s*\d+(?:[.,]\d+)?)*(?![\w])")
UNIT_RE = re.compile(r"\b(?:м2|м²|м3|м³|мп|м\.п|п\.м|шт|маш|смена|кг|т|мм|см|м)\b", re.IGNORECASE)
UNCERTAINTY_TERMS = (
    "нет явного",
    "нет общего",
    "неясн",
    "сомнен",
    "требует",
    "проверк",
    "не уверен",
    "нельзя",
    "не удалось",
    "оставлено null",
    "оставлен null",
    "компонент",
    "кандидат",
    "candidate",
    "needs_review",
    "missing",
)

MAX_TEXT = 900
IGNORED_NULL_KEYS = {
    # Derived/technical helper fields. Their absence is not a second-pass extraction task when
    # the row already contains the real project quantity.
    "code",
    "item_id",
    "kg_per_meter",
    "source_row_id",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def short(value: Any, limit: int = MAX_TEXT) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def normalize_text(value: Any) -> str:
    return str(value or "").lower().replace("ё", "е")


def has_numberish_text(*values: Any) -> bool:
    text = " ".join(short(v, 4000) for v in values if v not in (None, ""))
    return bool(NUMBER_RE.search(text) or UNIT_RE.search(text))


def has_uncertainty_text(*values: Any) -> bool:
    text = normalize_text(" ".join(short(v, 4000) for v in values if v not in (None, "")))
    return any(term in text for term in UNCERTAINTY_TERMS)


def value_has_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, dict):
        return any(v is None or v == "" for v in value.values())
    if isinstance(value, list):
        return any(value_has_null(v) for v in value)
    return False


def value_has_actionable_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, dict):
        return any(
            key not in IGNORED_NULL_KEYS and (item_value is None or item_value == "")
            for key, item_value in value.items()
        )
    if isinstance(value, list):
        return any(value_has_actionable_null(item) for item in value)
    return False


def source_text(item: dict[str, Any]) -> str:
    parts = []
    if item.get("source_pdf"):
        parts.append(str(item["source_pdf"]))
    if item.get("page_number") is not None:
        parts.append(f"стр. {item['page_number']}")
    if item.get("page_title"):
        parts.append(str(item["page_title"]))
    if item.get("table_context"):
        parts.append(str(item["table_context"]))
    return " | ".join(parts)


def item_code(item: dict[str, Any]) -> str:
    return str(item.get("target_code") or item.get("group_code") or "raw_table_rows")


def item_identity(section_code: str, bucket: str, index: int, item: dict[str, Any]) -> str:
    value = item.get("value")
    if isinstance(value, dict):
        for key in (
            "zone_id",
            "item_id",
            "beam_id",
            "lintel_id",
            "code",
            "mark",
            "name",
            "role",
            "item_name",
        ):
            if value.get(key):
                return f"{section_code}.{bucket}.{item_code(item)}.{value[key]}"
    if item.get("item_name"):
        return f"{section_code}.{bucket}.{item_code(item)}.{item['item_name']}"
    return f"{section_code}.{bucket}.{index}"


def candidate_summary(candidates: Any) -> list[dict[str, Any]]:
    result = []
    for candidate in candidates or []:
        if not isinstance(candidate, dict):
            continue
        result.append(
            {
                "target_code": candidate.get("target_code"),
                "group_code": candidate.get("group_code"),
                "item_name": candidate.get("item_name"),
                "value": candidate.get("value"),
                "unit": candidate.get("unit"),
                "normalized_unit": candidate.get("normalized_unit"),
                "source": source_text(candidate),
                "raw_text": short(candidate.get("raw_text"), 500),
                "notes": short(candidate.get("notes"), 500),
            }
        )
    return result


def task_reason(bucket: str, item: dict[str, Any]) -> str | None:
    value = item.get("value")
    notes = item.get("notes")
    raw_text = item.get("raw_text")
    candidates = item.get("candidates")

    if bucket == "missing":
        return "missing_target"
    if item.get("needs_review") or bucket == "needs_review":
        return "needs_review"
    if candidates:
        return "has_candidates"
    if value_has_actionable_null(value) and has_numberish_text(notes, candidates):
        return "null_value_with_numeric_evidence"
    if notes and has_uncertainty_text(notes):
        return "uncertain_note"
    if bucket == "raw_table_rows":
        mapped = item.get("mapped_target_codes") or item.get("target_code") or item.get("group_code")
        if not mapped and has_numberish_text(raw_text, notes):
            return "unmapped_numeric_raw_row"
        if notes and has_uncertainty_text(notes):
            return "raw_row_with_uncertainty"
    try:
        confidence = float(item.get("confidence"))
    except (TypeError, ValueError):
        confidence = None
    if confidence is not None and confidence < 0.85:
        return "low_confidence"
    return None


def iter_section_items(section: dict[str, Any]):
    for bucket in ("needs_review", "found", "missing", "raw_table_rows"):
        for index, item in enumerate(section.get(bucket) or [], start=1):
            if isinstance(item, dict):
                yield bucket, index, item


def build_tasks(extraction: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for section_code, section in (extraction.get("sections") or {}).items():
        if not isinstance(section, dict):
            continue
        for bucket, index, item in iter_section_items(section):
            reason = task_reason(bucket, item)
            if not reason:
                continue
            identity = item_identity(section_code, bucket, index, item)
            # found and needs_review often contain the same physical item twice. The packet is a
            # task list, not a faithful bucket dump, so dedupe across buckets.
            dedupe_key = json.dumps(
                [
                    section_code,
                    item_code(item),
                    item.get("item_name"),
                    item.get("value"),
                    item.get("raw_text"),
                    item.get("notes"),
                ],
                ensure_ascii=False,
                sort_keys=True,
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            tasks.append(
                {
                    "task_id": f"T{len(tasks) + 1:03d}",
                    "reason": reason,
                    "section_code": section_code,
                    "bucket": bucket,
                    "identity": identity,
                    "target_code": item.get("target_code"),
                    "group_code": item.get("group_code"),
                    "item_name": item.get("item_name"),
                    "value": item.get("value"),
                    "unit": item.get("unit"),
                    "normalized_unit": item.get("normalized_unit"),
                    "confidence": item.get("confidence"),
                    "needs_review": item.get("needs_review"),
                    "source": source_text(item),
                    "raw_text": short(item.get("raw_text")),
                    "notes": short(item.get("notes")),
                    "candidates": candidate_summary(item.get("candidates")),
                    "instruction": (
                        "Re-open the cited PDF place and decide whether a fact seen in notes/raw_text/"
                        "candidates should be moved into a structured JSON field, left as needs_review, "
                        "or left unchanged because the PDF does not support it."
                    ),
                }
            )
    return tasks


def write_markdown(tasks: list[dict[str, Any]], input_path: Path, output_path: Path) -> None:
    lines = [
        "# Universal extraction correction packet",
        "",
        f"Source JSON: `{input_path}`",
        "",
        "This packet is generated by code. It does not decide values and does not contain project-specific hints.",
        "Use it with `experiments/chat_extraction_poc/prompts/extraction_second_pass_correction_prompt.md`.",
        "",
        f"Tasks: {len(tasks)}",
        "",
    ]
    by_reason: dict[str, int] = {}
    for task in tasks:
        by_reason[task["reason"]] = by_reason.get(task["reason"], 0) + 1
    for reason, count in sorted(by_reason.items()):
        lines.append(f"- `{reason}`: {count}")
    lines.append("")

    for task in tasks:
        title_bits = [task["task_id"], task["reason"], task["section_code"]]
        if task.get("target_code") or task.get("group_code"):
            title_bits.append(str(task.get("target_code") or task.get("group_code")))
        lines.extend(
            [
                f"## {' / '.join(title_bits)}",
                "",
                f"- Bucket: `{task['bucket']}`",
                f"- Identity: `{task['identity']}`",
                f"- Item name: {task.get('item_name') or ''}",
                f"- Value: `{short(task.get('value'), 700)}`",
                f"- Unit: `{task.get('unit') or ''}` / normalized `{task.get('normalized_unit') or ''}`",
                f"- Confidence: `{task.get('confidence') or ''}`; needs_review: `{task.get('needs_review')}`",
                f"- Source: {task.get('source') or ''}",
                f"- Raw text: {task.get('raw_text') or ''}",
                f"- Notes: {task.get('notes') or ''}",
            ]
        )
        if task.get("candidates"):
            lines.append("- Candidates:")
            for candidate in task["candidates"]:
                lines.append(f"  - `{short(candidate, 900)}`")
        lines.extend(["", f"Action: {task['instruction']}", ""])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_json(tasks: list[dict[str, Any]], input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_json": str(input_path),
        "task_count": len(tasks),
        "tasks": tasks,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_correction_packet.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Extraction JSON from chat/API.")
    parser.add_argument("--output", type=Path, help="Markdown correction packet path.")
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional machine-readable JSON packet path. Defaults to sibling *_correction_packet.json.",
    )
    args = parser.parse_args()

    extraction = load_json(args.input)
    tasks = build_tasks(extraction)
    md_output = args.output or default_output_path(args.input)
    json_output = args.json_output or md_output.with_suffix(".json")
    write_markdown(tasks, args.input, md_output)
    write_json(tasks, args.input, json_output)
    print(
        json.dumps(
            {
                "input": str(args.input),
                "output": str(md_output),
                "json_output": str(json_output),
                "task_count": len(tasks),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
