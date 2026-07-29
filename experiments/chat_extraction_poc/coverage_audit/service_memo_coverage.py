"""Service-memo coverage check for a chat-extraction run.

Every needs_review item (across all sections) is a doubtful/uncertain spot the estimator (Elena)
should see and decide on. This script checks whether each needs_review item's target_code/group_code
appears literally somewhere in the service memo (служебная записка) text — a plain substring search,
not a semantic one.

This is a heuristic, not a proof: a needs_review item can genuinely be covered by memo prose that
never spells out the exact code (a false negative here), and a code appearing in the memo doesn't
guarantee the memo actually explains *this specific* row correctly (not checked at all). Treat "not
found" as "verify this one by hand," not as a confirmed bug — and don't trust "found" as a substitute
for actually reading the memo.

Does not fix or reinterpret anything, only reports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_needs_review(extraction: dict) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for section_code, section in (extraction.get("sections") or {}).items():
        for item in section.get("needs_review") or []:
            if not isinstance(item, dict):
                continue
            code = item.get("group_code") or item.get("target_code")
            if not code:
                continue
            rows.append(
                {
                    "section_code": section_code,
                    "code": code,
                    "item_name": item.get("item_name"),
                    "raw_text": item.get("raw_text") or "",
                    "notes": item.get("notes") or "",
                }
            )
    return rows


def check_coverage(needs_review_rows: list[dict[str, Any]], memo_text: str) -> list[dict[str, Any]]:
    memo_lower = memo_text.lower()
    # Group rows by code first: several rows of the same group_code (e.g. multiple
    # communications_pipe_items) only need ONE mention of that code in the memo, not one per row.
    by_code: dict[str, list[dict[str, Any]]] = {}
    for row in needs_review_rows:
        by_code.setdefault(row["code"], []).append(row)

    results = []
    for code, rows in sorted(by_code.items()):
        mentioned = code.lower() in memo_lower
        results.append(
            {
                "code": code,
                "section_codes": sorted({r["section_code"] for r in rows}),
                "row_count": len(rows),
                "mentioned_in_memo": mentioned,
                "sample_raw_text": rows[0]["raw_text"][:150],
            }
        )
    return results


def render_report(results: list[dict[str, Any]], extraction_path: Path, memo_path: Path) -> str:
    lines = ["# Service-memo coverage check", ""]
    lines.append(f"Extraction file: `{extraction_path}`")
    lines.append(f"Service memo: `{memo_path}`")
    lines.append("")
    lines.append(
        "Heuristic: literal substring search for each needs_review code inside the memo text. "
        "Not found = verify by hand, not a confirmed bug. Found = code is mentioned somewhere, "
        "doesn't guarantee the explanation is correct or complete."
    )
    lines.append("")

    total = len(results)
    not_mentioned = [r for r in results if not r["mentioned_in_memo"]]
    lines.append(f"Distinct needs_review codes: {total}. Not found in memo: {len(not_mentioned)}.")
    lines.append("")

    if not_mentioned:
        lines.append("## Not found in service memo — verify by hand")
        lines.append("")
        for r in not_mentioned:
            lines.append(
                f"- `{r['code']}` (section(s): {', '.join(r['section_codes'])}, {r['row_count']} row(s)) "
                f"— sample source: \"{r['sample_raw_text']}\""
            )
        lines.append("")

    lines.append("## Found in service memo")
    lines.append("")
    for r in results:
        if r["mentioned_in_memo"]:
            lines.append(f"- `{r['code']}` (section(s): {', '.join(r['section_codes'])}, {r['row_count']} row(s))")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Path to a real extraction_output.json")
    parser.add_argument("--memo", type=Path, required=True, help="Path to the service memo .txt")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    extraction = load_json(args.input)
    memo_text = args.memo.read_text(encoding="utf-8")

    needs_review_rows = collect_needs_review(extraction)
    results = check_coverage(needs_review_rows, memo_text)
    report = render_report(results, args.input, args.memo)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")

    not_mentioned_count = sum(1 for r in results if not r["mentioned_in_memo"])
    print(f"checked: {len(results)} distinct needs_review codes, {not_mentioned_count} not found in memo -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
