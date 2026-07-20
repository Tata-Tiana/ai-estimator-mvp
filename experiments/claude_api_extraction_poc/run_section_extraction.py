"""Run Claude API extraction for selected sections and prepared pages."""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(*args: Any, **kwargs: Any) -> bool:  # type: ignore[no-redef]
        return False


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
PACK_DIR = HERE / "pack"

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
ANTHROPIC_VERSION = os.getenv("ANTHROPIC_VERSION", "2023-06-01")
REQUEST_TIMEOUT_S = 900
RETRY_COUNT = 2
RETRY_SLEEP_S = 10

PACK_FILES = [
    PACK_DIR / "prompts" / "api_estimate_extraction_prompt.md",
    PACK_DIR / "schemas" / "claude_extraction_output_schema.json",
    PACK_DIR / "data" / "calculator_targets_compact.json",
    PACK_DIR / "data" / "target_aliases_ru.yaml",
    PACK_DIR / "data" / "unit_normalization_guide.json",
    PACK_DIR / "data" / "section_guide.json",
]


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_page_ref(ref: str) -> tuple[str, int]:
    if ":" not in ref:
        raise ValueError(f"page ref must look like 'source.pdf:23', got: {ref}")
    source_pdf, page_number = ref.rsplit(":", 1)
    return source_pdf, int(page_number)


def select_pages(manifest: dict[str, Any], page_refs: list[str]) -> list[dict[str, Any]]:
    wanted = {parse_page_ref(ref) for ref in page_refs}
    selected = [
        page
        for page in manifest.get("pages", [])
        if (page["source_pdf"], int(page["page_number"])) in wanted
    ]
    found = {(page["source_pdf"], int(page["page_number"])) for page in selected}
    missing = sorted(wanted - found)
    if missing:
        raise ValueError(f"page refs not found in manifest: {missing}")
    return selected


def build_pack_text() -> str:
    parts = [
        "Ниже локальный API extraction pack. Используй только эти правила и выбранные страницы.",
        "",
    ]
    for path in PACK_FILES:
        if not path.exists():
            raise FileNotFoundError(f"missing pack file: {path}")
        rel = path.relative_to(PACK_DIR)
        parts.extend([f"===== FILE: {rel} =====", read_text(path), f"===== END FILE: {rel} =====", ""])
    return "\n".join(parts)


def page_text_block(pages: list[dict[str, Any]]) -> str:
    parts = ["# SELECTED PREPARED PAGES"]
    for page in pages:
        text = read_text(Path(page["text_path"]))
        parts.extend(
            [
                "",
                f"## PAGE_REF: {page['source_pdf']}:{page['page_number']}",
                f"- source_pdf: {page['source_pdf']}",
                f"- page_number: {page['page_number']}",
                f"- title_guess: {page.get('title_guess')}",
                f"- text_chars: {page.get('text_chars')}",
                "",
                "```text",
                text,
                "```",
            ]
        )
    return "\n".join(parts)


def image_block(page: dict[str, Any]) -> dict[str, Any]:
    image_path = Path(page["image_path"])
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": data,
        },
    }


def compact_inventory_text(inventory_path: Path | None) -> str:
    if not inventory_path:
        return ""
    inventory = read_json(inventory_path)
    compact_candidates: list[dict[str, Any]] = []
    for candidate in inventory.get("candidates") or []:
        has_alias = bool(candidate.get("alias_hits"))
        has_numbers = bool(candidate.get("numbers"))
        is_contextual_table_row = (
            candidate.get("source_type") == "pdfplumber_table_row"
            and has_numbers
            and len(str(candidate.get("text") or "")) > 20
        )
        if not has_alias and not is_contextual_table_row:
            continue
        compact_candidates.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "source_type": candidate.get("source_type"),
                "source_pdf": candidate.get("source_pdf"),
                "page_number": candidate.get("page_number"),
                "text": candidate.get("text"),
                "numbers": candidate.get("numbers") or [],
                "alias_hits": candidate.get("alias_hits") or [],
                "table_index": candidate.get("table_index"),
                "row_index": candidate.get("row_index"),
                "cells": candidate.get("cells"),
            }
        )
    compact = {
        "method": inventory.get("method"),
        "pages": inventory.get("pages"),
        "target_hit_counts": inventory.get("target_hit_counts"),
        "candidates": compact_candidates,
    }
    return "\n".join(
        [
            "# PREPARED PAGE INVENTORY",
            "Ниже нейтральная машинная подготовка страниц. Это не готовый ответ и не источник истины.",
            "Используй inventory как указатель на строки-кандидаты, но проверяй значения по изображению страницы.",
            "Если inventory и изображение расходятся, приоритет у изображения, а строку отметь needs_review.",
            "",
            "```json",
            json.dumps(compact, ensure_ascii=False, indent=2),
            "```",
        ]
    )


def build_request_text(section_codes: list[str], pages: list[dict[str, Any]], inventory_path: Path | None) -> str:
    sections = ", ".join(section_codes)
    return "\n\n".join(
        [part for part in [
            build_pack_text(),
            "# API SECTION RUN",
            f"requested_section_codes: {sections}",
            (
                "Извлеки только перечисленные requested_section_codes. "
                "Верни частичный extraction_output JSON с верхним ключом `sections`, "
                "где есть только эти разделы, затем служебную записку. "
                "Сохраняй реальные русские названия таблиц из PDF в raw_table_rows[].table_title.\n\n"
                "Для секционного API-теста отвечай компактно:\n"
                "- не создавай extracted_values с value: null для каждого отсутствующего target;\n"
                "- отсутствующие target_code перечисляй в missing;\n"
                "- extracted_values должны содержать найденные значения и спорные найденные кандидаты;\n"
                "- raw_table_rows заполняй только по таблицам/строкам выбранных страниц, относящимся к requested_section_codes;\n"
                "- служебная записка должна описывать только выбранные страницы и явно сказать, что это partial section run."
            ),
            compact_inventory_text(inventory_path),
            page_text_block(pages),
        ] if part]
    )


def build_payload(
    manifest: dict[str, Any],
    pages: list[dict[str, Any]],
    section_codes: list[str],
    model: str,
    max_tokens: int,
    inventory_path: Path | None,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = []
    for page in pages:
        content.append(
            {
                "type": "text",
                "text": f"IMAGE_PAGE_REF: {page['source_pdf']}:{page['page_number']}",
            }
        )
        content.append(image_block(page))
    content.append(
        {
            "type": "text",
            "text": build_request_text(section_codes, pages, inventory_path),
        }
    )
    return {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": content}],
        "metadata": {
            "user_id": str(manifest.get("project_code") or "unknown_project"),
        },
    }


def call_anthropic(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            response = requests.post(
                f"{ANTHROPIC_BASE_URL.rstrip('/')}/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": ANTHROPIC_VERSION,
                    "content-type": "application/json",
                },
                json=payload,
                timeout=REQUEST_TIMEOUT_S,
            )
            if not response.ok:
                raise requests.HTTPError(
                    f"{response.status_code} error: {response.text}",
                    response=response,
                )
            return response.json()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < RETRY_COUNT:
                print(f"attempt {attempt}/{RETRY_COUNT} failed: {exc}")
                time.sleep(RETRY_SLEEP_S)
    assert last_error is not None
    raise last_error


def response_text(response_json: dict[str, Any]) -> str:
    chunks: list[str] = []
    for block in response_json.get("content") or []:
        if block.get("type") == "text":
            chunks.append(block.get("text") or "")
    return "\n".join(chunks).strip()


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def split_json_and_memo(text: str) -> tuple[dict[str, Any], str]:
    cleaned = text.lstrip()
    decoder = json.JSONDecoder()

    if cleaned.startswith("```"):
        fence_match = re.match(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
        if fence_match:
            return json.loads(fence_match.group(1)), cleaned[fence_match.end() :].strip()

    first_brace = cleaned.find("{")
    if first_brace < 0:
        raise ValueError("Could not find JSON object in Claude response text.")
    data, relative_end = decoder.raw_decode(cleaned[first_brace:])
    return data, cleaned[first_brace + relative_end :].strip()


def write_outputs(out_dir: Path, response_json: dict[str, Any]) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "api_raw_response.json"
    text_path = out_dir / "api_output_text.txt"
    extraction_path = out_dir / "extraction_output.json"
    memo_path = out_dir / "service_memo.txt"

    write_json(raw_path, response_json)
    text = response_text(response_json)
    text_path.write_text(text + "\n", encoding="utf-8")
    extraction, memo = split_json_and_memo(text)
    write_json(extraction_path, extraction)
    memo_path.write_text(strip_code_fence(memo) + "\n", encoding="utf-8")
    return extraction_path, memo_path


def write_dry_run(out_dir: Path, payload: dict[str, Any]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    dry_payload = dict(payload)
    dry_content = []
    for block in payload["messages"][0]["content"]:
        if block.get("type") == "image":
            clone = dict(block)
            clone["source"] = dict(block["source"])
            clone["source"]["data"] = f"<base64 omitted: {len(block['source']['data'])} chars>"
            dry_content.append(clone)
        elif block.get("type") == "text":
            dry_content.append({"type": "text", "text": f"<text omitted: {len(block['text'])} chars>"})
        else:
            dry_content.append(block)
    dry_payload["messages"] = [{"role": "user", "content": dry_content}]
    path = out_dir / "dry_run_payload_summary.json"
    write_json(path, dry_payload)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--section-code", action="append", required=True)
    parser.add_argument("--page-ref", action="append", required=True, help="Use 'source.pdf:page_number'.")
    parser.add_argument("--inventory", type=Path, help="Optional page_inventory.json from build_page_inventory.py.")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=40000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env()
    manifest = read_json(args.manifest)
    pages = select_pages(manifest, args.page_ref)
    payload = build_payload(manifest, pages, args.section_code, args.model, args.max_tokens, args.inventory)

    print("Claude API section extraction request")
    print(f"model: {args.model}")
    print(f"sections: {', '.join(args.section_code)}")
    print(f"pages: {len(pages)}")
    if args.inventory:
        print(f"inventory: {args.inventory}")
    print(f"pack_dir: {PACK_DIR}")

    if args.dry_run:
        path = write_dry_run(args.out_dir, payload)
        print(f"dry run -> {path}")
        return 0

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is empty. Add it to .env or export it before running without --dry-run.")

    response_json = call_anthropic(payload, api_key)
    extraction_path, memo_path = write_outputs(args.out_dir, response_json)
    print(f"extraction -> {extraction_path}")
    print(f"memo -> {memo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
