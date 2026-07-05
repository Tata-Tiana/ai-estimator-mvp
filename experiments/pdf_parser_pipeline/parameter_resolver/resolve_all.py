from __future__ import annotations

from typing import Any

from .resolver_engine import resolve


def resolve_all(
    schema: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    section_scope_mode: str = 'scored',
) -> list[dict[str, Any]]:
    """Resolve every parameter in the schema against a list of generic_candidates.

    Returns a flat list of result dicts, one per parameter across all sections.
    Parameters without resolver_hints get status='no_hints'.

    section_scope_mode: passed to resolver_engine.
      'scored' (default) — same-section candidates score higher;
                           unknown-section candidates flag needs_review.
      'off'              — no section adjustment (original behaviour).
    """
    results: list[dict[str, Any]] = []

    for section in schema:
        section_code = section['section_code']
        section_name = section['section_name']

        for param in section['parameters']:
            meta = {
                'section_code': section_code,
                'section_name': section_name,
                'parameter_code': param['parameter_code'],
                'calculator_input_key': param['calculator_input_key'],
                'label': param.get('label', ''),
                'unit': param.get('unit', ''),
            }

            if not param.get('resolver_hints'):
                results.append({
                    **meta,
                    'status': 'no_hints',
                    'value_decimal': None,
                    'raw_value': None,
                    'normalized_unit': None,
                    'source_candidate_id': None,
                    'evidence_id': None,
                    'raw_text': None,
                    'normalized_text': None,
                    'candidate_section_code': None,
                    'confidence': 0.0,
                    'needs_review': False,
                    'alternatives': [],
                    'reason': 'resolver_hints not defined for this parameter',
                })
                continue

            result = resolve(
                param,
                candidates,
                param_section_code=section_code,
                section_scope_mode=section_scope_mode,
            )
            results.append({**meta, **result})

    return results
