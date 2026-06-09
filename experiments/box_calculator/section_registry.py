from __future__ import annotations


SECTION_NAMES = {
    "foundation_slab": "Фундаментная плита",
    "load_bearing_walls_lintels": "Несущие стены и перемычки",
    "floor_slab_1": "Плита перекрытия 1-го этажа",
    "floor_slab_2": "Плита перекрытия 2-го этажа",
}

DEFAULT_METAL_SECTION_ORDER = [
    "foundation_slab",
    "load_bearing_walls_lintels",
    "floor_slab_1",
    "floor_slab_2",
]


def section_name(section_code: str) -> str:
    return SECTION_NAMES.get(section_code, section_code)
