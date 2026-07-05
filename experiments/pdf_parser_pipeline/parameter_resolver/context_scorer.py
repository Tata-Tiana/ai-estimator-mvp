from __future__ import annotations

import re
from typing import Any


def score_candidate(
    candidate: dict[str, Any],
    hints: dict[str, Any],
) -> tuple[float, str]:
    """Score a candidate against resolver_hints context rules.

    Returns (score, reason) where score=0.0 means rejected.

    positive_context — AND logic: ALL patterns must match.
    negative_context — OR logic:  ANY match rejects.
    prefer_context   — soft bonus: raises score, never rejects.

    Patterns are matched against normalized_text + subject_hint combined.
    """
    text = (
        (candidate.get('normalized_text') or '')
        + ' '
        + (candidate.get('subject_hint') or '')
    )

    # negative first: any match → reject immediately
    for pattern in hints.get('negative_context', []):
        if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
            return 0.0, f'negative_context matched: {pattern!r}'

    # positive: all must match (AND)
    missing: list[str] = []
    for pattern in hints.get('positive_context', []):
        if not re.search(pattern, text, re.IGNORECASE | re.UNICODE):
            missing.append(pattern)
    if missing:
        return 0.0, f'positive_context not matched: {missing}'

    # base score from extractor confidence
    score = float(candidate.get('confidence', 0.5))

    # prefer_context: soft bonus, never rejects
    for pattern in hints.get('prefer_context', []):
        if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
            score = min(1.0, score + 0.05)

    return score, 'context matched'
