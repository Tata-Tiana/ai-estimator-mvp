#!/usr/bin/env python3
"""Smoke: run resolve_all against generic_candidates from usv_strict_pdf_parser_v3.

Output: experiments/pdf_parser_pipeline/output/resolved_parameters.json
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.pdf_parser_pipeline.section_schema import get_section_schema
from experiments.pdf_parser_pipeline.parameter_resolver.resolve_all import resolve_all

_CANDIDATES_PATH = (
    Path(__file__).resolve().parent.parent
    / 'usv_strict_pdf_parser_v3/data/extracted/generic_candidates.json'
)
_OUTPUT_PATH = Path(__file__).resolve().parent / 'output/resolved_parameters.json'


def main() -> int:
    if not _CANDIDATES_PATH.exists():
        print(f'ERROR: candidates not found: {_CANDIDATES_PATH}')
        return 1

    candidates: list[dict] = json.loads(_CANDIDATES_PATH.read_text(encoding='utf-8'))
    schema = get_section_schema()
    results = resolve_all(schema, candidates)

    _OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    # ── section-level report ──────────────────────────────────────────────
    by_section: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_section[r['section_code']].append(r)

    print(f'\n=== resolve_all smoke: {len(results)} параметров, {len(candidates)} кандидатов ===\n')

    grand: dict[str, int] = defaultdict(int)
    for section_code, rows in by_section.items():
        cnt: dict[str, int] = defaultdict(int)
        for r in rows:
            cnt[r['status']] += 1
            if r.get('needs_review'):
                cnt['needs_review'] += 1
        section_name = rows[0]['section_name']
        print(f'  {section_name}')
        print(
            f'    total={len(rows)}'
            f'  found={cnt["found"]}'
            f'  missing={cnt["missing"]}'
            f'  no_hints={cnt["no_hints"]}'
            f'  needs_review={cnt["needs_review"]}'
        )
        for k, v in cnt.items():
            grand[k] += v
        grand['total'] += len(rows)

    print(
        f'\nИТОГО: {grand["total"]}'
        f'  found={grand["found"]}'
        f'  missing={grand["missing"]}'
        f'  no_hints={grand["no_hints"]}'
        f'  needs_review={grand["needs_review"]}'
    )
    print(f'\nSaved → {_OUTPUT_PATH}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
