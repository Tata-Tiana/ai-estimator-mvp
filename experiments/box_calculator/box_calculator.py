from __future__ import annotations

from typing import Any

from metal_delivery_allocator import MetalSection, allocate_metal_deliveries
from section_registry import DEFAULT_METAL_SECTION_ORDER, section_name


def _ordered_metal_sections(config: dict[str, Any]) -> list[MetalSection]:
    raw_sections = config.get("sections", [])
    if not isinstance(raw_sections, list):
        raise ValueError("metal_delivery.sections must be a list")

    section_order = config.get("section_order") or DEFAULT_METAL_SECTION_ORDER
    order_index = {section_code: index for index, section_code in enumerate(section_order)}

    sections = []
    for raw in raw_sections:
        section_code = raw["section_code"]
        sections.append(
            MetalSection(
                section_code=section_code,
                section_name=raw.get("section_name") or section_name(section_code),
                metal_weight_kg=float(raw.get("metal_weight_kg", 0)),
            )
        )

    return sorted(
        sections,
        key=lambda item: order_index.get(item.section_code, len(order_index)),
    )


def calculate_box(input_data: dict[str, Any]) -> dict[str, Any]:
    project_name = input_data.get("project_name", "")
    metal_config = input_data.get("metal_delivery", {})
    warnings = []

    result: dict[str, Any] = {
        "project_name": project_name,
        "warnings": warnings,
    }

    if not metal_config.get("enabled", False):
        warnings.append("metal_delivery is disabled")
        result["recommended_metal_delivery_allocation"] = None
        return result

    sections = _ordered_metal_sections(metal_config)
    allocation = allocate_metal_deliveries(
        sections=sections,
        capacity_kg=float(metal_config.get("capacity_kg", 10000)),
        unit_price=float(metal_config.get("unit_price", 0)),
    )
    result["recommended_metal_delivery_allocation"] = allocation
    warnings.extend(allocation.get("warnings", []))
    result["totals_policy"] = {
        "section_totals_recalculated": False,
        "metal_delivery_added_to_grand_total": False,
        "reason": (
            "legacy section totals may already include metal delivery; allocation is "
            "reported separately until exporter can replace legacy delivery lines."
        ),
    }
    return result
