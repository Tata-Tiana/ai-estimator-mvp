from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED_DIR = DATA_DIR / "extracted"
CANDIDATES_PATH = EXTRACTED_DIR / "candidates.json"


def evidence_id(payload: dict[str, Any]) -> str:
    raw = "|".join(
        str(payload.get(key, ""))
        for key in (
            "source_pdf",
            "physical_page_number",
            "logical_sheet_type",
            "candidate_type",
            "raw_label",
            "value",
            "unit",
            "raw_context",
        )
    )
    return "ev_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


class CandidateStore:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []
        self._seen: set[str] = set()

    def add(self, **payload: Any) -> dict[str, Any]:
        payload.setdefault("confidence", "medium")
        payload.setdefault("notes", "")
        payload["evidence_id"] = evidence_id(payload)
        if payload["evidence_id"] not in self._seen:
            self._seen.add(payload["evidence_id"])
            self.items.append(payload)
        return payload

    def extend(self, rows: list[dict[str, Any]]) -> None:
        for row in rows:
            self.add(**row)

    def write(self, path: Path = CANDIDATES_PATH) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path


def load_candidates(path: Path = CANDIDATES_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))
