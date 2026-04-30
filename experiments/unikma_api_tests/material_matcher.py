from __future__ import annotations

from typing import Any


def match_materials(
    material_list: list[str],
    unikma_data: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    results: dict[str, list[dict[str, Any]]] = {}

    for material in material_list:
        query = material.strip().lower()
        matches: list[dict[str, Any]] = []

        for item in unikma_data:
            haystack = " ".join(
                str(item.get(field, ""))
                for field in ("Name", "FullName", "Code", "FullCode")
            ).lower()
            if query and query in haystack:
                matches.append(item)
            if len(matches) >= 3:
                break

        results[material] = matches

    return results

