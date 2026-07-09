"""A6.0: run one OpenAI vision call per rendered page image.

Reads manifest.json produced by render_pdf_pages.py (one or more source
PDFs already merged into the same pages-dir), sends each page image with
the generic prompt from vision_schema.py, and writes one JSON object per
page to --out-json. No page is skipped or hand-picked; --max-pages exists
only as a dev/cost-control aid, default is "process everything in the
manifest".
"""
from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False

from vision_schema import PROMPT

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
REQUEST_TIMEOUT_S = 180
RETRY_COUNT = 3
RETRY_SLEEP_S = 5

LOGGER = logging.getLogger("vision_pdf_parser_poc")


def load_manifest(pages_dir: Path) -> list[dict]:
    manifest_path = pages_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No manifest.json in {pages_dir} — run render_pdf_pages.py first."
        )
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    return sorted(entries, key=lambda e: (e["source_pdf"], e["page_number"]))


def encode_image_data_url(image_path: Path) -> str:
    data = image_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def build_payload(model: str, image_data_url: str) -> dict:
    return {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": PROMPT},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
        "text": {"format": {"type": "json_object"}},
    }


def call_openai(payload: dict) -> dict:
    last_error: Exception | None = None
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            response = requests.post(
                f"{OPENAI_BASE_URL}/responses",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=REQUEST_TIMEOUT_S,
            )
            if not response.ok:
                raise requests.HTTPError(
                    f"{response.status_code} error: {response.text}", response=response
                )
            return response.json()
        except Exception as exc:  # noqa: BLE001 - retry on any transient failure
            last_error = exc
            if attempt < RETRY_COUNT:
                LOGGER.warning("vision call attempt %d/%d failed: %s", attempt, RETRY_COUNT, exc)
                time.sleep(RETRY_SLEEP_S)
    assert last_error is not None
    raise last_error


def extract_json_from_response(response_json: dict) -> dict:
    text_value = response_json.get("output_text")
    if text_value:
        return json.loads(clean_json_text(text_value))
    for item in response_json.get("output", []):
        for content_item in item.get("content", []):
            if content_item.get("type") == "output_text":
                return json.loads(clean_json_text(content_item.get("text", "")))
    raise ValueError("Could not extract JSON from OpenAI response.")


def clean_json_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


def extract_page(entry: dict, model: str, dry_run: bool) -> dict:
    image_path = Path(entry["image_path"])
    result: dict[str, Any] = {
        "source_pdf": entry["source_pdf"],
        "page_number": entry["page_number"],
        "image_path": str(image_path),
    }
    if dry_run:
        result["dry_run"] = True
        return result

    payload = build_payload(model, encode_image_data_url(image_path))
    try:
        response_json = call_openai(payload)
        parsed = extract_json_from_response(response_json)
        result["extracted"] = parsed
    except Exception as exc:  # noqa: BLE001 - one bad page must not abort the run
        result["error"] = str(exc)
        LOGGER.error("page %s/%s failed: %s", entry["source_pdf"], entry["page_number"], exc)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages-dir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-pages", type=int, default=None, help="dev/cost-control only, default: all pages")
    parser.add_argument("--dry-run", action="store_true", help="build requests without calling the API")
    args = parser.parse_args()

    if not args.dry_run and not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is empty. Add it to .env before running without --dry-run.")

    entries = load_manifest(args.pages_dir)
    if args.max_pages is not None:
        entries = entries[: args.max_pages]

    pages: list[dict] = []
    for i, entry in enumerate(entries, start=1):
        print(f"[{i}/{len(entries)}] {entry['source_pdf']} page {entry['page_number']}")
        pages.append(extract_page(entry, args.model, args.dry_run))

    output = {
        "model": args.model,
        "dry_run": args.dry_run,
        "pages_dir": str(args.pages_dir),
        "page_count": len(pages),
        "pages": pages,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failed = [p for p in pages if "error" in p]
    print(f"done: {len(pages)} pages, {len(failed)} failed -> {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
