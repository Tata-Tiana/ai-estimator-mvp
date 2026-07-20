"""Run the local API extraction pack through Anthropic Claude API.

This is the simple full-PDF API equivalent of the manual chat upload flow:
PDF project files + the local API prompt pack -> extraction_output.json +
service_memo.txt + validation_report.md.

It deliberately does not touch calculators, Google Sheets, adapters, or
production Telegram flow.
"""
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
    PACK_DIR / "README_FOR_CHAT_UPLOAD.md",
]


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_prompt_text() -> str:
    parts = [
        "Ниже загружены все файлы chat-extraction pack как текст.",
        "Используй их так, как если бы они были приложены отдельными файлами в чате.",
        "PDF проекта приложены отдельными document-блоками в этом же API-запросе.",
        "",
    ]
    for path in PACK_FILES:
        if not path.exists():
            raise FileNotFoundError(f"missing pack file: {path}")
        rel = path.relative_to(PACK_DIR)
        parts.extend(
            [
                f"===== FILE: {rel} =====",
                read_text(path),
                f"===== END FILE: {rel} =====",
                "",
            ]
        )
    parts.append(
        "Выполни извлечение по приложенным PDF. "
        "Верни сначала чистый JSON extraction_output.json, затем служебную записку отдельным текстовым блоком."
    )
    return "\n".join(parts)


def encode_pdf_block(pdf_path: Path) -> dict[str, Any]:
    data = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    return {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": data,
        },
        "title": pdf_path.name,
        "context": f"Project source PDF: {pdf_path.name}",
    }


def build_payload(pdf_paths: list[Path], model: str, max_tokens: int) -> dict[str, Any]:
    content: list[dict[str, Any]] = []
    for pdf_path in pdf_paths:
        content.append(encode_pdf_block(pdf_path))
    content.append({"type": "text", "text": build_prompt_text()})
    return {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": content}],
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
        except Exception as exc:  # noqa: BLE001 - transient API/network failures are retried
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
            json_text = fence_match.group(1)
            data = json.loads(json_text)
            memo = cleaned[fence_match.end() :].strip()
            return data, memo

    try:
        data, end = decoder.raw_decode(cleaned)
        memo = cleaned[end:].strip()
        return data, memo
    except json.JSONDecodeError:
        pass

    first_brace = cleaned.find("{")
    if first_brace < 0:
        raise ValueError("Could not find JSON object in Claude response text.")
    data, relative_end = decoder.raw_decode(cleaned[first_brace:])
    memo = cleaned[first_brace + relative_end :].strip()
    return data, memo


def write_outputs(out_dir: Path, response_json: dict[str, Any]) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "api_raw_response.json"
    text_path = out_dir / "api_output_text.txt"
    extraction_path = out_dir / "extraction_output.json"
    memo_path = out_dir / "service_memo.txt"

    raw_path.write_text(json.dumps(response_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    text = response_text(response_json)
    text_path.write_text(text + "\n", encoding="utf-8")
    extraction, memo = split_json_and_memo(text)
    extraction_path.write_text(json.dumps(extraction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    memo_path.write_text(strip_code_fence(memo) + "\n", encoding="utf-8")
    return extraction_path, memo_path


def validate_output(extraction_path: Path, report_path: Path) -> None:
    import sys

    sys.path.insert(0, str(HERE))
    from validate_claude_extraction import main as validate_main

    old_argv = list(sys.argv)
    try:
        sys.argv = [
            "validate_claude_extraction.py",
            "--input",
            str(extraction_path),
            "--report",
            str(report_path),
        ]
        validate_main()
    finally:
        sys.argv = old_argv


def describe_request(pdf_paths: list[Path], model: str, max_tokens: int) -> None:
    total_pdf_bytes = sum(path.stat().st_size for path in pdf_paths)
    print("Claude API extraction request")
    print(f"model: {model}")
    print(f"max_tokens: {max_tokens}")
    print(f"pdf_count: {len(pdf_paths)}")
    print(f"pdf_bytes_total: {total_pdf_bytes}")
    for path in pdf_paths:
        print(f"  - {path} ({path.stat().st_size} bytes)")
    print(f"pack_files: {len(PACK_FILES)}")
    print(f"pack_dir: {PACK_DIR}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", action="append", type=Path, required=True, help="Project PDF. Pass multiple times.")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=20000)
    parser.add_argument("--dry-run", action="store_true", help="Build and describe the request without calling API.")
    args = parser.parse_args()

    load_env()
    pdf_paths = [path.expanduser().resolve() for path in args.pdf]
    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

    describe_request(pdf_paths, args.model, args.max_tokens)
    payload = build_payload(pdf_paths, args.model, args.max_tokens)

    if args.dry_run:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        dry_payload = dict(payload)
        dry_content = []
        for block in payload["messages"][0]["content"]:
            if block.get("type") == "document":
                clone = dict(block)
                clone["source"] = dict(block["source"])
                clone["source"]["data"] = f"<base64 omitted: {len(block['source']['data'])} chars>"
                dry_content.append(clone)
            else:
                dry_content.append({"type": "text", "text": f"<prompt omitted: {len(block['text'])} chars>"})
        dry_payload["messages"] = [{"role": "user", "content": dry_content}]
        (args.out_dir / "dry_run_payload_summary.json").write_text(
            json.dumps(dry_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"dry run -> {args.out_dir / 'dry_run_payload_summary.json'}")
        return 0

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is empty. Add it to .env or export it before running without --dry-run.")

    response_json = call_anthropic(payload, api_key)
    extraction_path, memo_path = write_outputs(args.out_dir, response_json)
    report_path = args.out_dir / "validation_report.md"
    validate_output(extraction_path, report_path)
    print(f"extraction -> {extraction_path}")
    print(f"memo -> {memo_path}")
    print(f"validation -> {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
