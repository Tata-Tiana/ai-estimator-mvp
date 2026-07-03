from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import parser_paths
from text_normalization import normalize_text


def _row_text(cells: list[str]) -> str:
    return ' | '.join(c.strip() for c in cells if c and c.strip())


def _build_evidence_from_data(
    logical_pages: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    drawing_index: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build evidence list from pre-loaded data structures.

    Separated from build_evidence_layer() so tests can pass synthetic data
    without touching the filesystem."""
    evidence: list[dict[str, Any]] = []
    counter = 0

    # Index page metadata by (source_pdf, physical_page_number) for table enrichment
    page_meta: dict[tuple[str, int], dict[str, Any]] = {
        (p['source_pdf'], p['physical_page_number']): p
        for p in logical_pages
    }

    # ── 1. Page text evidence ───────────────────────────────────────────────
    for page in logical_pages:
        raw = (page.get('raw_page_text') or '').strip()
        if not raw:
            continue
        counter += 1
        evidence.append({
            'evidence_id': f'ev_{counter:06d}',
            'source_pdf': page['source_pdf'],
            'physical_page_number': page['physical_page_number'],
            'drawing_sheet_number': page.get('drawing_sheet_number') or '',
            'logical_sheet_title': page.get('logical_sheet_title') or '',
            'logical_sheet_type': page.get('logical_sheet_type') or 'unknown',
            'table_index': None,
            'row_index': None,
            'source_kind': 'page_text',
            'raw_text': raw,
            'normalized_text': normalize_text(raw),
            'meta': {
                'table_headers': [],
                'neighbor_cells': [],
                'previous_row_text': '',
                'next_row_text': '',
            },
        })

    # ── 2. Logical sheet titles (separate evidence for title-only keyword hits) ─
    seen_titles: set[tuple[str, str]] = set()
    for page in logical_pages:
        title = (page.get('logical_sheet_title') or '').strip()
        if not title:
            continue
        key = (page['source_pdf'], title)
        if key in seen_titles:
            continue
        seen_titles.add(key)
        counter += 1
        evidence.append({
            'evidence_id': f'ev_{counter:06d}',
            'source_pdf': page['source_pdf'],
            'physical_page_number': page['physical_page_number'],
            'drawing_sheet_number': page.get('drawing_sheet_number') or '',
            'logical_sheet_title': title,
            'logical_sheet_type': page.get('logical_sheet_type') or 'unknown',
            'table_index': None,
            'row_index': None,
            'source_kind': 'logical_sheet_title',
            'raw_text': title,
            'normalized_text': normalize_text(title),
            'meta': {
                'table_headers': [],
                'neighbor_cells': [],
                'previous_row_text': '',
                'next_row_text': '',
            },
        })

    # ── 3. Table row evidence ───────────────────────────────────────────────
    # Critical: tables are the primary source when page text is empty (e.g. CAD PDFs
    # that encode text only in table structures, not in the page text stream).
    for table in tables:
        src_pdf = table['source_pdf']
        page_num = table['physical_page_number']
        t_idx = table['table_index']
        rows: list[list[str]] = table.get('rows') or []

        meta_page = page_meta.get((src_pdf, page_num), {})
        logical_title = meta_page.get('logical_sheet_title') or ''
        logical_type = meta_page.get('logical_sheet_type') or 'unknown'
        drawing_num = meta_page.get('drawing_sheet_number') or ''

        # First non-empty row used as potential header context
        headers: list[str] = []
        for row in rows:
            candidate_headers = [c.strip() for c in row if c and c.strip()]
            if candidate_headers:
                headers = candidate_headers
                break

        for row_idx, row in enumerate(rows):
            raw = _row_text(row)
            if not raw:
                continue

            prev_text = _row_text(rows[row_idx - 1]) if row_idx > 0 else ''
            next_text = _row_text(rows[row_idx + 1]) if row_idx < len(rows) - 1 else ''

            counter += 1
            evidence.append({
                'evidence_id': f'ev_{counter:06d}',
                'source_pdf': src_pdf,
                'physical_page_number': page_num,
                'drawing_sheet_number': drawing_num,
                'logical_sheet_title': logical_title,
                'logical_sheet_type': logical_type,
                'table_index': t_idx,
                'row_index': row_idx,
                'source_kind': 'table_row',
                'raw_text': raw,
                'normalized_text': normalize_text(raw),
                'meta': {
                    'table_headers': headers,
                    'neighbor_cells': [c.strip() for c in row],
                    'previous_row_text': prev_text,
                    'next_row_text': next_text,
                },
            })

    # ── 4. Drawing index evidence ───────────────────────────────────────────
    for entry in (drawing_index or []):
        text = entry.get('evidence_text') or entry.get('drawing_sheet_title') or ''
        if not text:
            continue
        counter += 1
        evidence.append({
            'evidence_id': f'ev_{counter:06d}',
            'source_pdf': entry.get('source_pdf') or '',
            'physical_page_number': entry.get('physical_page_number'),
            'drawing_sheet_number': entry.get('drawing_sheet_number') or '',
            'logical_sheet_title': entry.get('drawing_sheet_title') or '',
            'logical_sheet_type': 'drawing_index',
            'table_index': None,
            'row_index': None,
            'source_kind': 'drawing_index',
            'raw_text': text,
            'normalized_text': normalize_text(text),
            'meta': {
                'table_headers': [],
                'neighbor_cells': [],
                'previous_row_text': '',
                'next_row_text': '',
            },
        })

    return evidence


def build_evidence_layer() -> list[dict[str, Any]]:
    """Read logical_pages.json, tables.json and drawing_index.json (if present),
    produce evidence.json in the extracted/ directory.

    Tables are treated as a primary source – if page text is empty but tables
    exist, evidence is still created from table rows."""
    logical_pages_path = parser_paths.logical_pages_path()
    tables_path = parser_paths.tables_path()
    drawing_index_path = parser_paths.drawing_index_path()

    logical_pages: list[dict[str, Any]] = (
        json.loads(logical_pages_path.read_text(encoding='utf-8'))
        if logical_pages_path.exists()
        else []
    )
    tables: list[dict[str, Any]] = (
        json.loads(tables_path.read_text(encoding='utf-8'))
        if tables_path.exists()
        else []
    )
    drawing_index: list[dict[str, Any]] = (
        json.loads(drawing_index_path.read_text(encoding='utf-8'))
        if drawing_index_path.exists()
        else []
    )

    evidence = _build_evidence_from_data(logical_pages, tables, drawing_index)

    dest = parser_paths.evidence_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return evidence


def main() -> int:
    ev = build_evidence_layer()
    print(f'evidence: {parser_paths.evidence_path()} ({len(ev)} items)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
