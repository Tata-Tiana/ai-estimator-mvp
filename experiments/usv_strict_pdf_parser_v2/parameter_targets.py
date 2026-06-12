from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAPPED_DIR = DATA_DIR / "mapped"
TARGETS_PATH = MAPPED_DIR / "parameter_targets.json"


SECTION_CODES = {
    "Земляные работы": "earthworks",
    "Фундаментная плита": "foundation_slab",
    "Гидроизоляция": "waterproofing",
    "Несущие стены и перемычки": "load_bearing_walls_lintels",
    "Плита перекрытия 1-го этажа": "floor_slab_1",
    "Плита перекрытия 2-го этажа": "floor_slab_2",
    "Плоская кровля": "flat_roof",
    "Вентиляционные каналы Schiedel": "schiedel_vent_channels",
}


@dataclass(frozen=True)
class Target:
    section_name: str
    calculator_input_key: str
    label: str
    required_status: str
    unit: str
    required_for_calculation: bool
    show_to_elena: bool
    mapping_hints: dict[str, Any]

    @property
    def section_code(self) -> str:
        return SECTION_CODES[self.section_name]


def target(section: str, key: str, label: str, status: str, unit: str, keywords: list[str], page_titles: list[str] | None = None) -> Target:
    return Target(
        section_name=section,
        calculator_input_key=key,
        label=label,
        required_status=status,
        unit=unit,
        required_for_calculation=status in {"AUTO_PROJECT", "SUPPLIER_INPUT", "MANUAL_REQUIRED"},
        show_to_elena=True,
        mapping_hints={"keywords": keywords, "units": [unit] if unit else [], "page_titles": page_titles or []},
    )


def build_targets() -> list[dict[str, Any]]:
    targets = [
        target("Земляные работы", "pit_area_m2", "Площадь котлована", "AUTO_PROJECT", "м2", ["площадь", "котлован"], ["котлован"]),
        target("Земляные работы", "geotextile_laying_area_m2", "Площадь геотекстиля", "AUTO_PROJECT", "м2", ["геотекст"], ["котлован"]),
        target("Земляные работы", "sand_volume_m3", "Объем песка", "AUTO_PROJECT", "м3", ["песок"], ["котлован"]),
        target("Земляные работы", "trench_routes", "Таблица траншей", "AUTO_PROJECT", "м3", ["транше", "к1"], ["котлован"]),
        target("Фундаментная плита", "concrete_volume_m3", "Бетон фундаментной плиты", "AUTO_PROJECT", "м3", ["бетон"], ["фундамент"]),
        target("Фундаментная плита", "eps100_edge_volume_m3", "ЭППС 100 мм торец фундаментной плиты", "AUTO_PROJECT", "м3", ["эппс", "100", "торец"], ["фундамент"]),
        target("Фундаментная плита", "eps50_bottom_volume_m3", "ЭППС 50 мм низ фундаментной плиты", "AUTO_PROJECT", "м3", ["эппс", "50"], ["фундамент"]),
        target("Фундаментная плита", "slab_side_formwork_area_m2", "Площадь боковой опалубки фундаментной плиты", "AUTO_PROJECT", "м2", ["площадь", "опалуб"], ["фундамент"]),
        target("Фундаментная плита", "edge_insulation_area_m2", "Площадь утепления торцов фундаментной плиты", "AUTO_PROJECT", "м2", ["утеплен", "торц"], ["фундамент"]),
        target("Фундаментная плита", "thermal_insert_100_material_spec_qty", "ЭППС 100 мм термовставки", "AUTO_PROJECT", "м3", ["эппс", "100", "термовстав"], ["термовстав"]),
        target("Фундаментная плита", "thermal_insert_50_material_spec_qty", "ЭППС 50 мм термовставки", "AUTO_PROJECT", "м3", ["эппс", "50", "термовстав"], ["термовстав"]),
        target("Фундаментная плита", "thermal_insert_length_m", "Длина термовставок", "AUTO_PROJECT", "м/п", ["длина", "термовстав"], ["термовстав"]),
        target("Гидроизоляция", "cutoff_waterproofing_load_bearing_walls_area_m2", "Отсечная гидроизоляция несущих стен", "AUTO_PROJECT", "м2", ["гидроизоля", "несущ"], ["гидроизоля"]),
        target("Гидроизоляция", "cutoff_waterproofing_partitions_area_m2", "Отсечная гидроизоляция перегородок", "AUTO_PROJECT", "м2", ["гидроизоля", "перегород"], ["гидроизоля"]),
        target("Несущие стены и перемычки", "lintel_total_length_m", "Длина перемычек в U-блоках", "AUTO_PROJECT", "м/п", ["перемыч", "u"], ["перемыч"]),
        target("Несущие стены и перемычки", "lintel_concrete_spec_volume_m3", "Бетон перемычек", "AUTO_PROJECT", "м3", ["бетон", "перемыч"], ["перемыч"]),
        target("Несущие стены и перемычки", "vent_chimney_gas_block_spec_volume_m3", "Газоблок для обкладки вентканалов", "AUTO_PROJECT", "м3", ["газобет", "обклад"], ["вент"]),
        target("Несущие стены и перемычки", "floor_2_masonry_volume_m3", "Объем кладки несущих стен 2-го этажа", "AUTO_PROJECT", "м3", ["несущ", "стен"], ["газобет"]),
        target("Плита перекрытия 1-го этажа", "slab_concrete_volume_m3", "Бетон плиты +3.480", "AUTO_PROJECT", "м3", ["бетон", "плит"], ["3.480"]),
        target("Плита перекрытия 1-го этажа", "beams_concrete_volume_m3", "Бетон балок +3.480", "AUTO_PROJECT", "м3", ["бетон", "бал"], ["3.480"]),
        target("Плита перекрытия 1-го этажа", "main_formwork_area_m2", "Площадь опалубки под плиту 1-го этажа", "AUTO_PROJECT", "м2", ["опалуб"], ["3.480"]),
        target("Плита перекрытия 1-го этажа", "edge_formwork_area_m2", "Площадь торцевой опалубки плиты 1-го этажа", "AUTO_PROJECT", "м2", ["торц", "опалуб"], ["3.480"]),
        target("Плита перекрытия 1-го этажа", "beams_formwork_area_m2", "Площадь опалубки балок", "AUTO_PROJECT", "м2", ["бал", "опалуб"], ["3.480"]),
        target("Плита перекрытия 1-го этажа", "bottom_slab_eps_work_area_m2", "Площадь утепления низа плиты", "AUTO_PROJECT", "м2", ["эппс", "низ"], ["3.480"]),
        target("Плита перекрытия 1-го этажа", "slab_edge_eps_material_area_m2", "Площадь утепления торца плиты", "AUTO_PROJECT", "м2", ["эппс", "торец"], ["3.480"]),
        target("Плита перекрытия 2-го этажа", "slab_concrete_volume_m3", "Бетон плиты +4.680", "AUTO_PROJECT", "м3", ["бетон"], ["4.680"]),
        target("Плита перекрытия 2-го этажа", "main_formwork_area_m2", "Площадь опалубки плиты 2-го этажа", "AUTO_PROJECT", "м2", ["площадь", "опалуб"], ["4.680"]),
        target("Плита перекрытия 2-го этажа", "edge_formwork_area_m2", "Площадь торцевой опалубки плиты 2-го этажа", "AUTO_PROJECT", "м2", ["торец", "опалуб"], ["4.680"]),
        target("Плита перекрытия 2-го этажа", "edge_insulation_area_m2", "Площадь утепления торца плиты 2-го этажа", "AUTO_PROJECT", "м2", ["эппс", "торец"], ["4.680"]),
        target("Плоская кровля", "roof_area_level_1_m2", "Площадь кровли уровня +3.480", "AUTO_PROJECT", "м2", ["площадь", "кровл", "3.480"], ["кровл"]),
        target("Плоская кровля", "roof_area_level_2_m2", "Площадь кровли уровня +4.680", "AUTO_PROJECT", "м2", ["площадь", "кровл", "4.680"], ["кровл"]),
        target("Плоская кровля", "parapet_abutment_length_m", "Длина примыкания к парапетам", "AUTO_PROJECT", "м/п", ["примыкан", "парапет"], ["кровл"]),
        target("Плоская кровля", "wall_abutment_length_m", "Длина примыкания к стенам", "AUTO_PROJECT", "м/п", ["примыкан", "стен"], ["кровл"]),
        target("Плоская кровля", "eps50_supplier_required_volume_m3", "ЭППС кровли по раскладке поставщика", "SUPPLIER_INPUT", "м3", ["carbon", "prof"], ["кровл"]),
        target("Плоская кровля", "slope_plates_supplier_layout", "Разуклонка кровли", "SUPPLIER_INPUT", "", ["разуклон", "уточнить"], ["кровл"]),
        target("Плоская кровля", "internal_roof_drains_count", "Внутренние воронки", "AUTO_PROJECT", "шт", ["внутрен", "ворон"], ["кровл"]),
        target("Плоская кровля", "parapet_roof_drains_count", "Парапетные воронки", "AUTO_PROJECT", "шт", ["парапет", "ворон"], ["кровл"]),
        target("Вентиляционные каналы Schiedel", "schiedel_vent_2_count", "Schiedel VENT 2", "AUTO_PROJECT", "шт", ["schiedel vent 2"], ["вент"]),
        target("Вентиляционные каналы Schiedel", "schiedel_vent_3_count", "Schiedel VENT 3", "AUTO_PROJECT", "шт", ["schiedel vent 3"], ["вент"]),
        target("Вентиляционные каналы Schiedel", "vent_chimney_gas_block_spec_volume_m3", "Газоблок обкладки вентканалов", "AUTO_PROJECT", "м3", ["газобет", "600", "150", "250"], ["вент"]),
        target("Вентиляционные каналы Schiedel", "schiedel_masonry_total_length_m", "Общая длина кладки вентканалов", "AUTO_PROJECT", "м/п", ["общая", "длина", "кладк"], ["вент"]),
    ]
    result = []
    for item in targets:
        payload = asdict(item)
        payload["section_code"] = item.section_code
        result.append(payload)
    return result


def write_targets() -> list[dict[str, Any]]:
    MAPPED_DIR.mkdir(parents=True, exist_ok=True)
    targets = build_targets()
    TARGETS_PATH.write_text(json.dumps(targets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return targets


def main() -> int:
    targets = write_targets()
    print(f"parameter_targets: {TARGETS_PATH} ({len(targets)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
