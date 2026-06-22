from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import parser_paths


INDEX_LINE_RE = re.compile(r"(?P<num>\d{1,3})\s+(?P<title>(?:План|Схема|Спецификация|Разрез|Узлы|Ведомость).{3,120})", re.IGNORECASE)


def load_pages() -> list[dict[str, Any]]:
    return json.loads(parser_paths.pages_text_path().read_text(encoding="utf-8"))


def build_drawing_index() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for page in load_pages():
        text = page.get("raw_page_text", "")
        if "ведомость" not in text.lower() and "лист" not in text.lower():
            continue
        for line in text.splitlines():
            match = INDEX_LINE_RE.search(line.strip())
            if not match:
                continue
            title = match.group("title").strip(" .")
            key = (page["source_pdf"], match.group("num"), title.lower())
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "source_pdf": page["source_pdf"],
                    "drawing_sheet_number": match.group("num"),
                    "drawing_sheet_title": title,
                    "physical_page_number": page["physical_page_number"],
                    "evidence_text": line.strip(),
                }
            )
    parser_paths.drawing_index_path().write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows


def main() -> int:
    rows = build_drawing_index()
    print(f"drawing_index: {parser_paths.drawing_index_path()} ({len(rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
