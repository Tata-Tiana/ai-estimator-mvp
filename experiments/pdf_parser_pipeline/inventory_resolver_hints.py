"""A5.1 step 2 — resolver_hints inventory (diagnostic only, no code changes).

Cross-references the 8-section calculator schema against the June-2026
human-confirmed parameter audit to find:

  1. AUTO_PROJECT parameters that still have no resolver_hints (the list to
     write hints for next).
  2. Non-AUTO_PROJECT parameters that nonetheless look like they might have
     real evidence in a PDF (reclassification_candidates) — detected with a
     throwaway, in-memory probe hint run through the real resolver, never
     written to section_schema.py.

Does not modify section_schema.py, generic_candidate_extractor.py,
resolver_engine.py, or any resolved parameter. Read-only diagnostic.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO_ROOT / 'experiments/usv_strict_pdf_parser_v3'))

from section_schema import get_section_schema  # noqa: E402
from parameter_resolver.resolver_engine import resolve  # noqa: E402

ELENA_AUDIT_MD = REPO_ROOT / 'docs/elena_parameter_review_pack_audit.md'
SCRIPT_AUDIT_XLSX = REPO_ROOT / 'experiments/parameter_audit/output/mvp_usv_demo/parameter_audit_result.xlsx'
USV_CANDIDATES = REPO_ROOT / 'experiments/usv_strict_pdf_parser_v3/data/extracted/generic_candidates.json'
TRC_CANDIDATES = REPO_ROOT / 'experiments/usv_strict_pdf_parser_v3/data_trc/extracted/generic_candidates.json'
REPORT_PATH = REPO_ROOT / 'experiments/pdf_parser_pipeline/reports/a5_1_resolver_hints_inventory.md'

# ── unit vocabulary translation (schema uses Cyrillic labels; resolver
# hints must use the internal normalized_unit codes from text_normalization.py) ──
_UNIT_TO_NORMALIZED: dict[str, str | None] = {
    'м3': 'm3', 'м2': 'm2', 'м': 'm', 'мм': 'mm', 'кг': 'kg',
    'шт': 'pcs', 'мп': 'linear_m', 'отм.': 'm',
    '-': None, 'bool': None, 'руб.': None, 'смена': None, 'рейс': None,
    'руб/мп': None, 'руб/м3': None, 'коэфф.': None,
}
_UNIT_TO_KIND: dict[str, str | None] = {
    'm3': 'volume', 'm2': 'area', 'linear_m': 'linear_length',
    'kg': 'weight', 'pcs': 'quantity', 'mm': 'diameter', 'm': None,
}

_HUMAN_AUDIT_CATEGORIES = (
    'SUPPLIER_INPUT',
    'DEPRECATED / LEGACY_ONLY',
    'DEPRECATED / OPTIONAL_OVERRIDE',
    'AUTO_PROJECT high risk',
)
_CATEGORY_LABEL = {
    'SUPPLIER_INPUT': 'SUPPLIER_INPUT',
    'DEPRECATED / LEGACY_ONLY': 'DEPRECATED_LEGACY_ONLY',
    'DEPRECATED / OPTIONAL_OVERRIDE': 'DEPRECATED_OPTIONAL_OVERRIDE',
    'AUTO_PROJECT high risk': 'AUTO_PROJECT',
}

_STOPWORDS = {
    'для', 'или', 'если', 'при', 'под', 'над', 'без', 'это', 'все', 'всех',
    'его', 'она', 'они', 'что', 'как', 'уже', 'еще', 'ещё', 'раз', 'ряд',
    'на', 'по', 'из', 'от', 'до', 'не', 'со', 'во', 'то', 'же', 'об',
}

# Domain words too generic to use ALONE as a probe keyword — they appear in
# dozens of unrelated parameters/candidates across a section (found via a
# first run of this script: e.g. "арматура" alone matched the same one
# candidate for 3 different rebar diameter/class/weight parameters at once).
# If keyword_from_label() has nothing left after removing these, it returns
# None and the parameter is not probed at all, rather than probing with an
# unreliable generic term.
_GENERIC_DOMAIN_WORDS = {
    'арматура', 'арматуры', 'арматуре', 'арматурой',
    'бетон', 'бетона', 'бетону',
    'газоблок', 'газоблока', 'газобетон', 'газобетона', 'блок', 'блока',
    'площадь', 'площади', 'объем', 'объём', 'объема', 'объёма',
    'длина', 'длины', 'высота', 'высоты', 'ширина', 'ширины',
    'количество', 'вес', 'весом', 'спецификация', 'спецификации',
    'участок', 'участка', 'поверхность', 'поверхности', 'устройство',
    'устройства', 'элемент', 'элемента',
}


def parse_elena_audit(path: Path) -> dict[tuple[str, str], str]:
    """Parse the human-confirmed June audit markdown into
    {(section_name_ru, calculator_input_key): audit_category}.

    Only 4 of 8 elena_decision categories are itemized by parameter in this
    doc (SUPPLIER_INPUT, DEPRECATED/LEGACY_ONLY, DEPRECATED/OPTIONAL_OVERRIDE,
    AUTO_PROJECT) — the rest (AUTO_CALCULATED/DEFAULT_VALUE/MATERIAL_CATALOG/
    OPTIONAL_CONTROL, 114 rows) only have aggregate counts in this file, not
    per-parameter identity. Those parameters fall through to the script
    fallback or 'not_audited'.
    """
    text = path.read_text(encoding='utf-8')
    sections = re.split(r'^## ', text, flags=re.MULTILINE)
    bullet_re = re.compile(r'^- (?P<section>.+?) :: `(?P<key>[^`]+)`', re.MULTILINE)

    mapping: dict[tuple[str, str], str] = {}
    for sec in sections[1:]:
        lines = sec.split('\n')
        title = lines[0].strip()
        if title not in _HUMAN_AUDIT_CATEGORIES:
            continue
        category = _CATEGORY_LABEL[title]
        body = '\n'.join(lines[1:])
        for m in bullet_re.finditer(body):
            mapping[(m.group('section').strip(), m.group('key').strip())] = category
    return mapping


def parse_script_audit_fallback(path: Path) -> dict[tuple[str, str], str]:
    """Parse the June-3 script (pre-human-review) audit xlsx as a fallback
    signal for parameters not itemized in the human-confirmed markdown.

    Keyed by (section_code, calculator_input_key) -> recommended_source_status.
    Not human-confirmed — always reported as 'script_suggested:<status>'.
    """
    if not path.exists():
        return {}
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb['all_parameters_audit']
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(v) for v in rows[0]]
    idx = {h: i for i, h in enumerate(headers)}
    mapping: dict[tuple[str, str], str] = {}
    for row in rows[1:]:
        section_code = row[idx['section_code']]
        key = row[idx['calculator_input_key']]
        status = row[idx['recommended_source_status']]
        if section_code and key:
            mapping[(section_code, key)] = status
    return mapping


def keywords_from_label(label: str) -> list[str]:
    """Extract up to 2 distinctive keywords from a parameter label for a
    loose detection probe. Not used for real hints — only for the throwaway
    reclassification-candidate scan.

    Generic domain words (арматура/бетон/газоблок/площадь/...) are excluded:
    used alone, they match the same unrelated candidate across dozens of
    different parameters (found empirically on the first run of this
    script). If nothing distinctive remains, returns [] and the parameter
    is not probed at all — a missed detection is safer than a noisy one.
    """
    words = re.findall(r'[а-яё]{4,}', label.lower())
    words = [w for w in words if w not in _STOPWORDS and w not in _GENERIC_DOMAIN_WORDS]
    if not words:
        return []
    # Prefer longer, more specific words; keep up to 2 distinct ones so the
    # probe uses AND logic (both must match) where possible — tighter than
    # a single generic-ish word, still generic (no project-specific values).
    uniq = sorted(set(words), key=len, reverse=True)
    return uniq[:2]


def build_priority(param: dict[str, Any]) -> str:
    """Heuristic P0/P1/P2 sort — a working sort order, not ground truth.

    P0: required, top-level scalar (no list index / nested dot) — the
        calculator cannot compute its section total without it.
    P1: required but a nested/indexed sub-field (e.g. rebar_items[0].x), or
        not required but still a real project quantity.
    P2: input_type == control_only, or clearly secondary.
    """
    key = param.get('calculator_input_key', '')
    required = bool(param.get('required'))
    input_type = param.get('input_type', '')
    if input_type == 'control_only':
        return 'P2'
    is_nested = bool(re.search(r'\[\d+\]|\.', key))
    if required and not is_nested:
        return 'P0'
    if required and is_nested:
        return 'P1'
    return 'P1' if required else 'P2'


def load_candidates(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else []


def probe_reclassification(
    param: dict[str, Any],
    candidates_by_project: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Throwaway probe: build a minimal in-memory resolver_hints dict (never
    written to section_schema.py) and run it through the REAL resolve()
    function against real candidates. Loose by design (no candidate_types
    restriction, no expected_kind filter) — favors recall over precision;
    every hit must be reviewed by a human, not auto-trusted."""
    unit = param.get('unit', '')
    normalized_unit = _UNIT_TO_NORMALIZED.get(unit)
    if not normalized_unit:
        return []
    keywords = keywords_from_label(param.get('label', ''))
    if not keywords:
        return []

    probe_hints = {
        'expected_unit': normalized_unit,
        'positive_context': [re.escape(k) for k in keywords],
        'min_confidence': 0.0,
    }
    probe_param = {'parameter_code': param['parameter_code'], 'resolver_hints': probe_hints}

    hits = []
    for project, candidates in candidates_by_project.items():
        result = resolve(probe_param, candidates, param_section_code=param['section_code'])
        if result['status'] == 'found':
            hits.append({'project': project, **result})
    return hits


def build_inventory() -> dict[str, Any]:
    schema = get_section_schema()
    human_audit = parse_elena_audit(ELENA_AUDIT_MD)
    script_audit = parse_script_audit_fallback(SCRIPT_AUDIT_XLSX)
    candidates_by_project = {
        'USV': load_candidates(USV_CANDIDATES),
        'TRC': load_candidates(TRC_CANDIDATES),
    }

    rows: list[dict[str, Any]] = []
    for section in schema:
        section_code = section['section_code']
        section_name = section['section_name']
        for param in section['parameters']:
            param = {**param, 'section_code': section_code, 'section_name': section_name}
            key = param['calculator_input_key']
            has_hints = bool(param.get('resolver_hints'))

            human_category = human_audit.get((section_name, key))
            if human_category:
                audit_source = 'human_confirmed'
                audit_category = human_category
            else:
                script_status = script_audit.get((section_code, key))
                if script_status:
                    audit_source = 'script_suggested'
                    audit_category = f'script_suggested:{script_status}'
                else:
                    audit_source = 'none'
                    audit_category = 'not_audited'

            priority = build_priority(param) if human_category == 'AUTO_PROJECT' else ''
            should_have_hints = (
                human_category == 'AUTO_PROJECT' and priority in ('P0', 'P1') and not has_hints
            )

            row = {
                'section_code': section_code,
                'section_name': section_name,
                'parameter_code': param.get('parameter_code', ''),
                'calculator_input_key': key,
                'label': param.get('label', ''),
                'unit': param.get('unit', ''),
                'schema_input_type': param.get('input_type', ''),
                'required': bool(param.get('required')),
                'has_resolver_hints': has_hints,
                'audit_source': audit_source,
                'audit_category': audit_category,
                'priority': priority,
                'should_have_resolver_hints': should_have_hints,
            }

            # Reclassification probe: only for non-AUTO_PROJECT params the
            # schema itself already tags as 'parsed' (i.e. schema's own,
            # pre-existing signal that this was meant to come from a PDF) —
            # scanning all 629 with a loose probe would be noisy without
            # this narrowing, and non-'parsed' types (price/calculated/
            # manual/control_only/default) are not what we are hunting for.
            if human_category != 'AUTO_PROJECT' and param.get('input_type') == 'parsed' and not has_hints:
                hits = probe_reclassification(param, candidates_by_project)
                if hits:
                    row['reclassification_hits'] = hits

            rows.append(row)

    return {'rows': rows, 'human_audit_count': len(human_audit), 'script_audit_count': len(script_audit)}


def render_report(data: dict[str, Any]) -> str:
    rows = data['rows']
    lines = ['# A5.1 — Resolver hints inventory', '']
    lines.append(
        f"Источник истины: `docs/elena_parameter_review_pack_audit.md` "
        f"({data['human_audit_count']} параметров с точной привязкой parameter_code, "
        f"из 4 категорий: AUTO_PROJECT/SUPPLIER_INPUT/DEPRECATED_LEGACY_ONLY/DEPRECATED_OPTIONAL_OVERRIDE — "
        f"остальные 4 категории июньского аудита (AUTO_CALCULATED/DEFAULT_VALUE/MATERIAL_CATALOG/OPTIONAL_CONTROL, "
        f"114 строк) в исходном markdown даны только агрегированными счётчиками, без parameter_code)."
    )
    lines.append(
        f"Fallback: `experiments/parameter_audit/output/mvp_usv_demo/parameter_audit_result.xlsx` "
        f"({data['script_audit_count']} строк, скриптовая эвристика от 3 июня, ДО человеческой проверки — "
        f"помечается как `script_suggested:*`, не как решение)."
    )
    lines.append('')

    # ── 3.1 general stats ──
    lines.append('## 3.1 Общая статистика по разделам')
    lines.append('')
    lines.append('| section_code | total_params | has_hints | auto_project_total | auto_project_with_hints | auto_project_without_hints |')
    lines.append('|---|---|---|---|---|---|')
    by_section: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_section[r['section_code']].append(r)
    for sc in sorted(by_section):
        srows = by_section[sc]
        total = len(srows)
        has_hints = sum(1 for r in srows if r['has_resolver_hints'])
        ap = [r for r in srows if r['audit_category'] == 'AUTO_PROJECT']
        ap_with = sum(1 for r in ap if r['has_resolver_hints'])
        lines.append(f"| {sc} | {total} | {has_hints} | {len(ap)} | {ap_with} | {len(ap) - ap_with} |")
    lines.append('')

    # ── 3.2 AUTO_PROJECT without hints ──
    lines.append('## 3.2 AUTO_PROJECT без resolver_hints')
    lines.append('')
    lines.append('Priority — рабочая сортировка (P0: required + top-level; P1: required+nested или '
                  'не required; P2: control_only), не истина.')
    lines.append('')
    lines.append('| section_code | parameter_code | display_name | unit | priority |')
    lines.append('|---|---|---|---|---|')
    missing_hints = [r for r in rows if r['audit_category'] == 'AUTO_PROJECT' and not r['has_resolver_hints']]
    for r in sorted(missing_hints, key=lambda r: (r['section_code'], r['priority'])):
        lines.append(f"| {r['section_code']} | {r['parameter_code']} | {r['label']} | {r['unit']} | {r['priority']} |")
    lines.append('')
    lines.append(f"Итого AUTO_PROJECT без hints: **{len(missing_hints)}** "
                 f"(P0: {sum(1 for r in missing_hints if r['priority']=='P0')}, "
                 f"P1: {sum(1 for r in missing_hints if r['priority']=='P1')}, "
                 f"P2: {sum(1 for r in missing_hints if r['priority']=='P2')})")
    lines.append('')

    # ── 3.3 not covered breakdown ──
    lines.append('## 3.3 Что не покрываем hints и почему')
    lines.append('')
    not_ap = [r for r in rows if r['audit_category'] != 'AUTO_PROJECT']
    cat_counter = Counter(r['audit_category'].split(':')[0] for r in not_ap)
    lines.append('| audit_category | count |')
    lines.append('|---|---|')
    for cat, cnt in cat_counter.most_common():
        lines.append(f"| {cat} | {cnt} |")
    lines.append('')
    lines.append(f"Итого не-AUTO_PROJECT: {len(not_ap)} (из них `not_audited`: "
                 f"{sum(1 for r in not_ap if r['audit_category']=='not_audited')} — "
                 f"вне 284 строк июньского human audit, статус не проверялся человеком).")
    lines.append('')

    # ── reclassification_candidates ──
    lines.append('## reclassification_candidates')
    lines.append('')
    lines.append(
        'Не-AUTO_PROJECT параметры с `schema_input_type=parsed` (уже существующий в схеме сигнал '
        '"задумывался как приходящий из PDF", независимо от июньского аудита), для которых '
        'черновой пробный hint (unit + 1 ключевое слово, никогда не сохранялся в section_schema.py) '
        'нашёл совпадение через настоящий `resolve()` на реальных кандидатах USV/TRC. '
        'Это сигнал для человека, не решение — статус НЕ меняется автоматически.'
    )
    lines.append('')
    # Group by the actual matched evidence (project, raw_text, value, unit) —
    # several sibling parameters (e.g. a list field's [0]..[15] variants) can
    # legitimately probe to the exact same one candidate. Showing that as
    # one row + a list of affected parameters is honest about what was
    # actually found (one piece of evidence), instead of implying N
    # independent discoveries.
    groups: dict[tuple, dict[str, Any]] = {}
    for r in rows:
        for hit in r.get('reclassification_hits', []):
            gkey = (hit['project'], hit.get('raw_text', ''), hit.get('value_decimal'), hit.get('normalized_unit'))
            g = groups.setdefault(gkey, {'hit': hit, 'params': []})
            g['params'].append((r['section_code'], r['parameter_code'], r['audit_category']))

    lines.append(f"Найдено уникальных совпадений: **{len(groups)}** "
                 f"(затрагивают {sum(len(g['params']) for g in groups.values())} параметров-кандидатов)")
    lines.append('')
    if groups:
        lines.append('| project | value | unit | confidence | affected_parameters (section :: code [audit_category]) | raw_text |')
        lines.append('|---|---|---|---|---|---|')
        for g in sorted(groups.values(), key=lambda g: -len(g['params'])):
            hit = g['hit']
            raw = (hit.get('raw_text') or '')[:100].replace('\n', ' ')
            params_str = '; '.join(f"{sc}::{pc} [{ac}]" for sc, pc, ac in g['params'])
            if len(g['params']) > 1:
                params_str = f"⚠ {len(g['params'])} параметров: " + params_str
            lines.append(
                f"| {hit['project']} | {hit.get('value_decimal')} | {hit.get('normalized_unit')} | "
                f"{hit.get('confidence')} | {params_str} | {raw} |"
            )
    lines.append('')
    lines.append(
        '⚠ = одно и то же свидетельство совпало сразу с несколькими параметрами — обычно значит, '
        'что вероятное ключевое слово всё ещё недостаточно специфично для этой группы параметров '
        '(например, однотипные позиции списка с одинаковым названием). Проверять такие строки '
        'осторожнее, чем строки с одним параметром.'
    )
    lines.append('')

    return '\n'.join(lines)


def main() -> int:
    data = build_inventory()
    report = render_report(data)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding='utf-8')
    print(f'inventory report written: {REPORT_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
