from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from generic_candidate_extractor import _has_useful_primary_quantity

_BASE_DIR = Path(__file__).resolve().parent

# Candidate types the resolver strips before scoring (A4.2.5.1 guard).
_AUXILIARY_TYPES = {'elevation_marker', 'diameter_spec'}

# ── Report-only diagnostic vocabulary ───────────────────────────────────────
# These regexes exist ONLY in this report script. They do not affect
# generic_candidate_extractor.py or logical_sheet_classifier.py, and they do
# not change section_code. Purpose: separate "classifier gap" unknowns from
# "no section exists yet for this content" unknowns, so A4.2.8 targets the
# right thing.
_PITCHED_ROOF_RE = re.compile(
    r'стропил|черепиц|мауэрлат|обрешет|контрбрус|кон[ье]к|аэроэлемент',
    re.IGNORECASE | re.UNICODE,
)
_ARCHITECTURAL_TITLE_RE = re.compile(
    r'фасад|цветовые решения|3d\s*вид|экспликация помещен|'
    r'ведомость оконных|ведомость дверных|срез .*этажа',
    re.IGNORECASE | re.UNICODE,
)


def _load(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else []


def _snippet(text: str, limit: int = 150) -> str:
    text = (text or '').replace('\n', ' ').strip()
    return text if len(text) <= limit else text[:limit] + ' …'


def _out_of_scope_reason(cand: dict[str, Any]) -> str | None:
    """Report-only bucket. Returns a reason string or None if in-scope."""
    title_haystack = ' '.join([
        cand.get('logical_sheet_title', '') or '',
        cand.get('table_context_title', '') or '',
    ])
    if _ARCHITECTURAL_TITLE_RE.search(title_haystack):
        return 'out_of_scope_architectural'
    text_haystack = ' '.join([cand.get('raw_text', '') or '', cand.get('normalized_text', '') or ''])
    if _PITCHED_ROOF_RE.search(text_haystack):
        return 'out_of_scope_pitched_roof'
    return None


class ProjectStats:
    def __init__(self, name: str, data_dir: Path):
        self.name = name
        self.data_dir = data_dir
        self.evidence = _load(data_dir / 'extracted' / 'evidence.json')
        self.candidates = _load(data_dir / 'extracted' / 'generic_candidates.json')
        resolved_path = data_dir / 'mapped' / 'resolved_parameters.json'
        self.resolved: list[dict[str, Any]] | None = (
            _load(resolved_path) if resolved_path.exists() else None
        )
        for c in self.candidates:
            c['_out_of_scope_reason'] = _out_of_scope_reason(c)

    # ── evidence ──
    def evidence_by_source_kind(self) -> Counter:
        return Counter(e.get('source_kind', 'unknown') for e in self.evidence)

    # ── candidates: core breakdowns ──
    def candidates_by_type(self) -> Counter:
        return Counter(c.get('candidate_type', 'unknown') for c in self.candidates)

    def auxiliary_count(self) -> int:
        return sum(1 for c in self.candidates if c.get('candidate_type') in _AUXILIARY_TYPES)

    def resolver_eligible_count(self) -> int:
        return len(self.candidates) - self.auxiliary_count()

    def by_section_code(self) -> Counter:
        return Counter(c.get('section_code', 'unknown') for c in self.candidates)

    def by_section_source(self) -> Counter:
        return Counter(c.get('section_source', 'unknown') for c in self.candidates)

    def out_of_scope_counts(self) -> Counter:
        return Counter(c['_out_of_scope_reason'] for c in self.candidates if c['_out_of_scope_reason'])

    # ── unknown audit ──
    def unknown_candidates(self) -> list[dict]:
        return [c for c in self.candidates if c.get('section_source') == 'unknown']

    def unknown_breakdown(self) -> Counter:
        cnt: Counter = Counter()
        for c in self.unknown_candidates():
            cnt[c['_out_of_scope_reason'] or 'unclassified'] += 1
        return cnt

    def unknown_unclassified_examples(self, limit: int = 10) -> list[dict]:
        """The genuine classifier-gap bucket: unknown, not explained by a
        known out-of-scope reason, and still resolver_eligible (i.e. would
        actually matter if a section existed for it)."""
        out = [
            c for c in self.unknown_candidates()
            if c['_out_of_scope_reason'] is None
            and c.get('candidate_type') not in _AUXILIARY_TYPES
        ]
        return out[:limit]

    # ── suspicious audit (A4.2.5.1 regression checks) ──
    def suspicious_audit(self) -> dict[str, list[dict]]:
        elevation_as_ordinary = [
            c for c in self.candidates
            if c.get('candidate_type') != 'elevation_marker'
            and c.get('value_candidates')
            and all(vc.get('kind') == 'elevation' for vc in c.get('value_candidates', []))
        ]
        diameter_only_as_route_summary = [
            c for c in self.candidates
            if c.get('candidate_type') == 'route_summary'
            and not _has_useful_primary_quantity(c.get('value_candidates', []))
        ]
        pipe_item_without_qty = [
            c for c in self.candidates
            if c.get('candidate_type') == 'pipe_item'
            and not _has_useful_primary_quantity(c.get('value_candidates', []))
        ]
        table_override = [c for c in self.candidates if c.get('section_source') == 'table_override']
        return {
            'elevation_as_ordinary_quantity': elevation_as_ordinary,
            'diameter_only_as_route_summary': diameter_only_as_route_summary,
            'pipe_item_without_primary_qty': pipe_item_without_qty,
            'table_override': table_override,
        }

    def examples_by_type(self, candidate_type: str, limit: int = 5) -> list[dict]:
        return [c for c in self.candidates if c.get('candidate_type') == candidate_type][:limit]

    def examples_by_section(self, limit_per_section: int = 1) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for c in self.candidates:
            sc = c.get('section_code', 'unknown')
            out.setdefault(sc, [])
            if len(out[sc]) < limit_per_section:
                out[sc].append(c)
        return out


# ── markdown rendering ──────────────────────────────────────────────────────

def _fmt_counter(counter: Counter, total: int | None = None) -> str:
    total = total if total is not None else sum(counter.values())
    lines = ['| Значение | Кол-во | Доля |', '|---|---|---|']
    for key, count in counter.most_common():
        pct = f'{count / total:.0%}' if total else '0%'
        lines.append(f'| {key} | {count} | {pct} |')
    return '\n'.join(lines)


def _fmt_example(c: dict[str, Any]) -> str:
    return (
        f"- `{c.get('candidate_id', '')}` **{c.get('candidate_type', '')}** "
        f"(section={c.get('section_code', 'unknown')}, source={c.get('section_source', 'unknown')}, "
        f"conf={c.get('confidence', 0)}) — {_snippet(c.get('raw_text', ''))}"
    )


def render_project_report(stats: ProjectStats) -> str:
    lines: list[str] = [f'## {stats.name}', '']

    lines.append(f'- Evidence total: **{len(stats.evidence)}**')
    lines.append(f'- Candidates total: **{len(stats.candidates)}**')
    lines.append(f'- resolver_eligible: **{stats.resolver_eligible_count()}**')
    lines.append(f'- auxiliary (elevation_marker + diameter_spec): **{stats.auxiliary_count()}**')
    if stats.resolved is not None:
        found = sum(1 for r in stats.resolved if r.get('status') == 'found')
        lines.append(f'- resolved_parameters: {len(stats.resolved)} (found={found})')
    else:
        lines.append('- resolved_parameters.json: not generated for this project')
    lines.append('')

    lines.append('### Evidence by source_kind')
    lines.append(_fmt_counter(stats.evidence_by_source_kind()))
    lines.append('')

    lines.append('### Candidates by candidate_type')
    lines.append(_fmt_counter(stats.candidates_by_type()))
    lines.append('')

    lines.append('### Candidates by section_code')
    lines.append(_fmt_counter(stats.by_section_code()))
    lines.append('')

    lines.append('### Candidates by section_source')
    lines.append(_fmt_counter(stats.by_section_source()))
    lines.append('')

    lines.append('### Out-of-scope (report-only diagnostic, not a section_code)')
    oos = stats.out_of_scope_counts()
    if oos:
        lines.append(_fmt_counter(oos, total=len(stats.candidates)))
    else:
        lines.append('_none_')
    lines.append('')

    lines.append('### Unknown audit (section_source == unknown)')
    unk = stats.unknown_candidates()
    lines.append(f'Total unknown: **{len(unk)}**')
    lines.append('')
    lines.append(_fmt_counter(stats.unknown_breakdown(), total=len(unk) or None))
    lines.append('')
    unclassified = stats.unknown_unclassified_examples()
    lines.append(f'`unclassified` examples (genuine classifier-gap candidates for A4.2.8), showing up to 10:')
    if unclassified:
        for c in unclassified:
            lines.append(_fmt_example(c))
    else:
        lines.append('_none_')
    lines.append('')

    lines.append('### Suspicious audit (A4.2.5.1 regression checks — expect ~0 outside table_override)')
    susp = stats.suspicious_audit()
    for key, items in susp.items():
        lines.append(f'- **{key}**: {len(items)}')
    for key, items in susp.items():
        if key == 'table_override':
            continue  # expected/benign, not a regression signal
        if items:
            lines.append('')
            lines.append(f'`{key}` examples:')
            for c in items[:5]:
                lines.append(_fmt_example(c))
    if susp['table_override']:
        lines.append('')
        lines.append('`table_override` examples:')
        for c in susp['table_override'][:5]:
            lines.append(_fmt_example(c))
    lines.append('')

    lines.append('### Examples by candidate_type')
    for ctype in ('elevation_marker', 'diameter_spec', 'pipe_item', 'pipe_piece_qty'):
        examples = stats.examples_by_type(ctype)
        lines.append(f'`{ctype}` (up to 5):')
        if examples:
            for c in examples:
                lines.append(_fmt_example(c))
        else:
            lines.append('_none_')
        lines.append('')

    lines.append('### Examples by section_code (1 per section)')
    for section, examples in stats.examples_by_section().items():
        for c in examples:
            lines.append(_fmt_example(c))
    lines.append('')

    return '\n'.join(lines)


def render_comparison(all_stats: list[ProjectStats]) -> str:
    lines = ['## Сравнение проектов', '']
    header = '| Метрика | ' + ' | '.join(s.name for s in all_stats) + ' |'
    sep = '|---|' + '---|' * len(all_stats)
    lines.append(header)
    lines.append(sep)

    def row(label: str, fn) -> str:
        return f'| {label} | ' + ' | '.join(str(fn(s)) for s in all_stats) + ' |'

    lines.append(row('Evidence total', lambda s: len(s.evidence)))
    lines.append(row('Candidates total', lambda s: len(s.candidates)))
    lines.append(row('resolver_eligible', lambda s: s.resolver_eligible_count()))
    lines.append(row('auxiliary', lambda s: s.auxiliary_count()))
    lines.append(row(
        'auxiliary %',
        lambda s: f'{s.auxiliary_count() / len(s.candidates):.0%}' if s.candidates else '0%',
    ))
    lines.append(row('unknown (section_source)', lambda s: len(s.unknown_candidates())))
    lines.append(row(
        'unknown %',
        lambda s: f'{len(s.unknown_candidates()) / len(s.candidates):.0%}' if s.candidates else '0%',
    ))
    lines.append(row(
        'out_of_scope_pitched_roof',
        lambda s: s.out_of_scope_counts().get('out_of_scope_pitched_roof', 0),
    ))
    lines.append(row(
        'out_of_scope_architectural',
        lambda s: s.out_of_scope_counts().get('out_of_scope_architectural', 0),
    ))
    lines.append(row(
        'unknown_unclassified',
        lambda s: s.unknown_breakdown().get('unclassified', 0),
    ))
    lines.append(row(
        'suspicious: elevation_as_ordinary',
        lambda s: len(s.suspicious_audit()['elevation_as_ordinary_quantity']),
    ))
    lines.append(row(
        'suspicious: diameter_only_as_route',
        lambda s: len(s.suspicious_audit()['diameter_only_as_route_summary']),
    ))
    lines.append(row(
        'suspicious: pipe_item_without_qty',
        lambda s: len(s.suspicious_audit()['pipe_item_without_primary_qty']),
    ))
    lines.append(row('table_override', lambda s: len(s.suspicious_audit()['table_override'])))
    lines.append('')
    return '\n'.join(lines)


def build_report(projects: list[tuple[str, Path]]) -> str:
    all_stats = [ProjectStats(name, _BASE_DIR / data_dir) for name, data_dir in projects]
    parts = ['# Smoke report', '']
    if len(all_stats) > 1:
        parts.append(render_comparison(all_stats))
    for stats in all_stats:
        parts.append(render_project_report(stats))
    return '\n'.join(parts)


def _parse_project_arg(value: str) -> tuple[str, Path]:
    name, _, data_dir = value.partition('=')
    if not _:
        raise argparse.ArgumentTypeError(f'expected NAME=DATA_DIR, got: {value}')
    return name, Path(data_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--project', dest='projects', action='append', type=_parse_project_arg,
        required=True, metavar='NAME=DATA_DIR',
        help='Repeatable. e.g. --project USV=data --project TRC=data_trc',
    )
    parser.add_argument('--out', type=Path, help='Write markdown report to this path')
    args = parser.parse_args()

    report = build_report(args.projects)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report + '\n', encoding='utf-8')
        print(f'smoke report written: {args.out}')
    else:
        print(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
