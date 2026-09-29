from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


_DATE_RE = re.compile(r"(?<!\d)\d{1,2}[.,_-]\d{1,2}[.,_-]\d{2,4}(?!\d)")
_COPY_SUFFIX_RE = re.compile(r"\s*\(\d+\)\s*$")
_DISCIPLINE_RE = re.compile(r"(?iu)(?:^|[\s_.-])(?:КР|КЖ|АР)[\s_.-]*[12](?=$|[\s_.-])")
_TOKEN_RE = re.compile(r"[0-9A-Za-zА-Яа-яЁё]+")
_NOISE_TOKENS = {
    "pdf",
    "для",
    "ии",
    "копия",
    "исправленный",
    "исправленная",
    "финал",
    "final",
}


def _source_file_tokens(filename: str) -> list[str]:
    stem = Path(str(filename)).stem
    stem = _COPY_SUFFIX_RE.sub("", stem)
    stem = _DATE_RE.sub(" ", stem)
    stem = _DISCIPLINE_RE.sub(" ", stem)
    return [token for token in _TOKEN_RE.findall(stem) if token.casefold() not in _NOISE_TOKENS]


def _common_tokens(token_lists: list[list[str]]) -> list[str]:
    if not token_lists:
        return []
    common = {token.casefold() for token in token_lists[0]}
    for tokens in token_lists[1:]:
        common &= {token.casefold() for token in tokens}
    return [token for token in token_lists[0] if token.casefold() in common]


def _safe_display_name(value: str, max_length: int = 80) -> str:
    value = re.sub(r"[\x00-\x1f/\\]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" ._-—")
    return value[:max_length].rstrip() or "Проект"


def project_label_from_sources(
    source_files: Iterable[Any] | None,
    *,
    fallback_filename: str = "",
    fallback_project_name: str = "",
) -> str:
    token_lists = [tokens for item in (source_files or []) if (tokens := _source_file_tokens(str(item)))]
    tokens = _common_tokens(token_lists) if len(token_lists) > 1 else (token_lists[0] if token_lists else [])
    if not tokens and token_lists:
        tokens = token_lists[0]
    if tokens:
        return _safe_display_name(" ".join(tokens))

    fallback_tokens = _source_file_tokens(fallback_filename)
    if fallback_tokens:
        return _safe_display_name(" ".join(fallback_tokens))
    return _safe_display_name(fallback_project_name)


def project_label_from_extraction(extraction: dict[str, Any], fallback_filename: str = "") -> str:
    return project_label_from_sources(
        extraction.get("source_files"),
        fallback_filename=fallback_filename,
        fallback_project_name=str(extraction.get("project_name") or ""),
    )


def project_drive_folder_name(project_label: str, created_at: str | datetime | None = None) -> str:
    if isinstance(created_at, datetime):
        created = created_at
    elif created_at:
        try:
            created = datetime.fromisoformat(str(created_at))
        except ValueError:
            created = datetime.now()
    else:
        created = datetime.now()
    return f"{_safe_display_name(project_label)} — {created.strftime('%d.%m.%Y')}"


def review_sheet_title(project_label: str, created_at: str | datetime | None = None) -> str:
    return f"Проверка — {project_drive_folder_name(project_label, created_at)}"
