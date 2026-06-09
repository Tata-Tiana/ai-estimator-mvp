from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any


@dataclass(frozen=True)
class MetalSection:
    section_code: str
    section_name: str
    metal_weight_kg: float


def allocate_metal_deliveries(
    sections: list[MetalSection],
    capacity_kg: float,
    unit_price: float,
) -> dict[str, Any]:
    if capacity_kg <= 0:
        raise ValueError("capacity_kg must be greater than 0")
    if unit_price < 0:
        raise ValueError("unit_price must be greater than or equal to 0")

    total_weight = sum(section.metal_weight_kg for section in sections)
    total_trucks = int(ceil(total_weight / capacity_kg)) if total_weight > 0 else 0

    allocation = []
    warnings = [
        "recommended_metal_delivery_allocation показан отдельно от итогов разделов; "
        "legacy section totals могут уже содержать доставку металла. Не добавлять "
        "allocation сверху, пока Excel exporter не поддерживает замену legacy-строки."
    ]
    cumulative_before = 0.0
    first_truck_allocated = False

    for section in sections:
        if section.metal_weight_kg < 0:
            raise ValueError(f"{section.section_code}.metal_weight_kg must be >= 0")

        cumulative_after = cumulative_before + section.metal_weight_kg
        allocated_trucks = 0

        if section.metal_weight_kg > 0 and not first_truck_allocated:
            allocated_trucks += 1
            first_truck_allocated = True

        for truck_number in range(2, total_trucks + 1):
            threshold = (truck_number - 1) * capacity_kg
            if cumulative_before <= threshold < cumulative_after:
                allocated_trucks += 1

        allocation.append(
            {
                "section_code": section.section_code,
                "section_name": section.section_name,
                "metal_weight_kg": round(section.metal_weight_kg, 4),
                "cumulative_weight_kg": round(cumulative_after, 4),
                "allocated_trucks": allocated_trucks,
                "delivery_cost": allocated_trucks * unit_price,
            }
        )
        cumulative_before = cumulative_after

    allocated_total = sum(item["allocated_trucks"] for item in allocation)
    if allocated_total != total_trucks:
        warnings.append(
            f"allocated_trucks total {allocated_total} differs from total_trucks {total_trucks}; check section order."
        )

    return {
        "capacity_kg": capacity_kg,
        "total_box_metal_weight_kg": round(total_weight, 4),
        "total_trucks": total_trucks,
        "unit_price": unit_price,
        "total_delivery_cost": total_trucks * unit_price,
        "section_order": [section.section_code for section in sections],
        "sections": allocation,
        "warnings": warnings,
    }
