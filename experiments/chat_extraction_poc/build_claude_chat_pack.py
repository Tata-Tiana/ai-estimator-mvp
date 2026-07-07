"""A6.1: package the generic prompt-pack for upload into a Claude chat.

Deliberately excludes anything project-specific or ground-truth: the
validated input.json, old parser outputs, comparison reports, and the
PDF itself (uploaded separately by the user). Everything included here
is generic infrastructure, safe to reuse for any project, not just USV.
"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

PACK_FILES = [
    HERE / "prompts" / "claude_estimate_extraction_prompt.md",
    HERE / "schemas" / "claude_extraction_output_schema.json",
    HERE / "data" / "calculator_targets_compact.json",
    HERE / "data" / "target_aliases_ru.yaml",
    HERE / "data" / "unit_normalization_guide.json",
    HERE / "data" / "section_guide.json",
    HERE / "README_FOR_CHAT_UPLOAD.md",
]


def build_pack(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in PACK_FILES:
            if not file_path.exists():
                raise FileNotFoundError(f"expected pack file missing: {file_path}")
            arcname = file_path.relative_to(HERE)
            zf.write(file_path, arcname)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "dist" / "claude_chat_extraction_pack.zip")
    args = parser.parse_args()

    build_pack(args.out)
    print(f"pack built -> {args.out}")
    print("contents:")
    for f in PACK_FILES:
        print(" ", f.relative_to(HERE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
