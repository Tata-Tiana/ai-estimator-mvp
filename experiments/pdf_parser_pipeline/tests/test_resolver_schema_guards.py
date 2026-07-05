"""Guards for the resolver_hints architecture contract.

ARCHITECTURE RULE (enforced here):
  A4 resolver_engine reads resolver_hints ONLY.
  It must NEVER read regex_patterns — that field is LEGACY.

Tests in this file verify two things:
  1. Schema-level: resolver_hints contain no bare project-specific numbers.
  2. Runtime-level: resolver_engine ignores regex_patterns (pending A4).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from experiments.pdf_parser_pipeline.section_schema import get_section_schema

# Project-specific bare numbers in context patterns.
# Product spec thicknesses/grades (50, 100, 150, 400, 500) are ALLOWED — they are
# part of material names (ЭППС 50мм, D400, термовставки 100мм) and are semantic.
# Flagged as suspicious:
#   - 4+ digit integers (≥ 1000): clearly measured quantities, not product specs
#   - Numbers with 2+ decimal places (40.53, 52.04): suspiciously precise measurements
_BARE_PROJECT_NUMBER = re.compile(
    r'^('
    r'\d{4,}([.,]\d+)?'   # 1000+ integers  (e.g. 1500, 2000)
    r'|'
    r'\d+[.,]\d{2,}'      # x.xx precision  (e.g. 40.53, 52.04, 142.40)
    r')$'
)


def test_resolver_hints_no_bare_project_numbers_in_context() -> None:
    """All resolver_hints positive/negative_context must be semantic patterns.

    Bare numbers like '1500', '162', '40.53' are project-specific values
    and must not appear as standalone context patterns. Domain terms like
    'ф12', 'А500С', 'ЭППС', '50' (product spec thickness) are allowed.
    """
    schema = get_section_schema()
    violations: list[str] = []

    for section in schema:
        for param in section['parameters']:
            hints = param.get('resolver_hints')
            if not hints:
                continue
            for field in ('positive_context', 'negative_context'):
                for pattern in hints.get(field, []):
                    if _BARE_PROJECT_NUMBER.match(pattern.strip()):
                        violations.append(
                            f"{section['section_code']}.{param['parameter_code']}"
                            f" → {field}: {pattern!r} looks like a bare project number"
                        )

    assert not violations, (
        'resolver_hints contain bare project-specific numbers — '
        'use semantic patterns (material names, units, keywords) instead:\n'
        + '\n'.join(f'  {v}' for v in violations)
    )


def test_resolver_hints_value_range_is_broad_sanity_check() -> None:
    """value_range must span at least one order of magnitude (ratio >= 10×).

    A narrow range like [1000, 2000] is project-specific reasoning.
    value_range is a sanity check, not a disambiguation tool —
    disambiguation belongs in positive_context / negative_context.
    """
    schema = get_section_schema()
    violations: list[str] = []

    for section in schema:
        for param in section['parameters']:
            hints = param.get('resolver_hints')
            if not hints:
                continue
            vr = hints.get('value_range')
            if not vr or len(vr) != 2:
                continue
            lo, hi = vr
            if lo <= 0:
                continue
            ratio = hi / lo
            if ratio < 10.0:
                violations.append(
                    f"{section['section_code']}.{param['parameter_code']}"
                    f" → value_range {vr} ratio={ratio:.1f}× (must be ≥10×)"
                )

    assert not violations, (
        'Narrow value_range detected — widen to a broad sanity check:\n'
        + '\n'.join(f'  {v}' for v in violations)
    )


@pytest.mark.skip(reason=(
    'Covered by test_resolver_engine.py::test_resolver_engine_ignores_regex_patterns_at_runtime '
    '(A4 implemented). This placeholder kept for traceability.'
))
def test_resolver_engine_ignores_regex_patterns_at_runtime() -> None:
    """Placeholder: resolver_engine must not use regex_patterns field.

    Implementation required in A4:
      - Create synthetic evidence with value matching regex_patterns but NOT
        matching resolver_hints (wrong unit/kind/context).
      - Run resolver_engine.resolve(param, candidates=[]).
      - Assert result == {'status': 'missing'}, not the regex-matched value.
    """
    raise NotImplementedError('implement after resolver_engine (A4) is created')
