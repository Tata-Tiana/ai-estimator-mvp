"""Contract-level ownership checks for foundation slab and grillage data.

This module is deliberately independent from the extraction prompt and calculators. It
checks the canonical repeated groups while the two contracts are being implemented
locally. Pipeline integration happens only after both calculators are ready.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


PIPELINE_DIR = Path(__file__).resolve().parent
SECTIONS_DIR = PIPELINE_DIR / "sections"


@dataclass(frozen=True)
class OwnershipIssue:
    code: str
    severity: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _load_ownership(section_code: str) -> dict[str, Any]:
    path = SECTIONS_DIR / section_code / "section_contract.yaml"
    contract = yaml.safe_load(path.read_text(encoding="utf-8"))
    return dict((contract.get("section") or {}).get("ownership") or {})


def _rows(payload: dict[str, Any], section_code: str, group_code: str) -> list[dict[str, Any]]:
    section = (payload.get("sections") or {}).get(section_code) or {}
    parameters = section.get("parameters") or {}
    group = parameters.get(group_code) or {}
    rows = group.get("rows") if isinstance(group, dict) else group
    return [dict(row) for row in (rows or []) if isinstance(row, dict)]


def _issue(code: str, severity: str, path: str, message: str) -> OwnershipIssue:
    return OwnershipIssue(code=code, severity=severity, path=path, message=message)


def _collect_elements(
    rows: list[dict[str, Any]],
    *,
    section_code: str,
    id_field: str,
    allowed_types: set[str],
    other_types: set[str],
) -> tuple[dict[str, dict[str, Any]], list[OwnershipIssue]]:
    found: dict[str, dict[str, Any]] = {}
    issues: list[OwnershipIssue] = []
    for index, row in enumerate(rows):
        path = f"sections.{section_code}.elements[{index}]"
        element_id = str(row.get(id_field) or "").strip()
        if not element_id:
            issues.append(_issue("missing_element_id", "needs_review", path, f"{id_field} is required"))
        elif element_id in found:
            issues.append(
                _issue("duplicate_element_id", "error", path, f"Duplicate {id_field}: {element_id}")
            )
        else:
            found[element_id] = row

        element_type = str(row.get("element_type") or "").strip()
        if not element_type:
            issues.append(
                _issue("missing_element_type", "needs_review", path, "element_type is required")
            )
        elif element_type not in allowed_types:
            if element_type in other_types:
                issues.append(
                    _issue(
                        "wrong_section_owner",
                        "error",
                        path,
                        f"{element_type} belongs to the other foundation section",
                    )
                )
            else:
                issues.append(
                    _issue(
                        "unknown_element_type",
                        "needs_review",
                        path,
                        f"Unknown element_type: {element_type}",
                    )
                )
    return found, issues


def audit_foundation_grillage_ownership(payload: dict[str, Any]) -> list[OwnershipIssue]:
    """Return errors and review flags without changing the supplied data."""

    slab_ownership = _load_ownership("foundation_slab")
    grillage_ownership = _load_ownership("grillage")
    slab_types = set(slab_ownership.get("element_types") or [])
    slab_rebar_types = set(slab_ownership.get("rebar_component_types") or [])
    grillage_types = set(grillage_ownership.get("element_types") or [])

    slab_rows = _rows(payload, "foundation_slab", "slab_zones")
    grillage_rows = _rows(payload, "grillage", "grillage_elements")
    slab_elements, issues = _collect_elements(
        slab_rows,
        section_code="foundation_slab",
        id_field="zone_id",
        allowed_types=slab_types,
        other_types=grillage_types,
    )
    grillage_elements, grillage_issues = _collect_elements(
        grillage_rows,
        section_code="grillage",
        id_field="element_id",
        allowed_types=grillage_types,
        other_types=slab_types,
    )
    issues.extend(grillage_issues)

    for element_id in sorted(set(slab_elements) & set(grillage_elements)):
        issues.append(
            _issue(
                "cross_section_id_collision",
                "error",
                "sections",
                f"Element id {element_id!r} is assigned to both foundation_slab and grillage",
            )
        )

    for index, row in enumerate(_rows(payload, "foundation_slab", "foundation_rebar_items")):
        path = f"sections.foundation_slab.foundation_rebar_items[{index}]"
        component = str(row.get("component") or "").strip()
        if not component:
            issues.append(
                _issue("missing_rebar_component", "needs_review", path, "component is required")
            )
        elif component not in slab_rebar_types:
            issues.append(
                _issue(
                    "wrong_rebar_owner",
                    "error",
                    path,
                    f"Foundation slab cannot own rebar component {component!r}",
                )
            )
        zone_id = str(row.get("zone_id") or "").strip()
        if zone_id and zone_id not in slab_elements:
            issues.append(
                _issue(
                    "orphan_rebar_owner",
                    "error",
                    path,
                    f"Unknown foundation slab zone_id: {zone_id}",
                )
            )

    for index, row in enumerate(_rows(payload, "grillage", "grillage_rebar_items")):
        path = f"sections.grillage.grillage_rebar_items[{index}]"
        element_id = str(row.get("element_id") or "").strip()
        if not element_id:
            issues.append(
                _issue(
                    "missing_rebar_owner",
                    "needs_review",
                    path,
                    "element_id is required unless the specification is explicitly common",
                )
            )
        elif element_id not in grillage_elements:
            issues.append(
                _issue(
                    "orphan_rebar_owner",
                    "error",
                    path,
                    f"Unknown grillage element_id: {element_id}",
                )
            )

    return issues


def assert_no_ownership_errors(payload: dict[str, Any]) -> list[OwnershipIssue]:
    """Raise for definite ownership violations, but preserve needs_review outcomes."""

    issues = audit_foundation_grillage_ownership(payload)
    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        details = "; ".join(f"{issue.code}: {issue.message}" for issue in errors)
        raise ValueError(details)
    return issues
