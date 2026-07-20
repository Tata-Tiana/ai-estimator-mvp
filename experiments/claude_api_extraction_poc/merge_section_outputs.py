"""Merge section API extraction outputs into final extraction files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def output_json_path(value: Path) -> Path:
    if value.is_dir():
        return value / "extraction_output.json"
    return value


def optional_memo_path(value: Path) -> Path | None:
    if value.is_dir():
        path = value / "service_memo.txt"
        return path if path.exists() else None
    path = value.with_name("service_memo.txt")
    return path if path.exists() else None


def merge_outputs(paths: list[Path]) -> tuple[dict[str, Any], str]:
    merged: dict[str, Any] = {
        "project_name": None,
        "source_files": [],
        "sections": {},
        "extraction_warnings": [],
    }
    source_files: list[Any] = []
    warnings: list[Any] = []
    memo_parts: list[str] = []

    for source in paths:
        json_path = output_json_path(source)
        if not json_path.exists():
            raise FileNotFoundError(json_path)
        data = read_json(json_path)

        if not merged["project_name"] and data.get("project_name"):
            merged["project_name"] = data.get("project_name")

        for item in data.get("source_files") or []:
            if item not in source_files:
                source_files.append(item)

        for section_code, section_data in (data.get("sections") or {}).items():
            if section_code in merged["sections"]:
                raise ValueError(f"duplicate section in inputs: {section_code}")
            merged["sections"][section_code] = section_data

        warnings.extend(data.get("extraction_warnings") or [])

        memo_path = optional_memo_path(source)
        if memo_path:
            memo_parts.append(f"===== {json_path.parent.name} =====\n{memo_path.read_text(encoding='utf-8').strip()}")

    merged["source_files"] = source_files
    merged["extraction_warnings"] = warnings
    memo = "\n\n".join(part for part in memo_parts if part.strip())
    return merged, memo


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--section-output",
        action="append",
        type=Path,
        required=True,
        help="Directory containing extraction_output.json or a direct JSON path.",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    extraction, memo = merge_outputs([path.resolve() for path in args.section_output])
    args.out_dir.mkdir(parents=True, exist_ok=True)
    extraction_path = args.out_dir / "extraction_output.json"
    memo_path = args.out_dir / "service_memo.txt"
    write_json(extraction_path, extraction)
    memo_path.write_text(memo + "\n", encoding="utf-8")

    print(f"sections: {len(extraction.get('sections') or {})}")
    print(f"extraction -> {extraction_path}")
    print(f"memo -> {memo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
