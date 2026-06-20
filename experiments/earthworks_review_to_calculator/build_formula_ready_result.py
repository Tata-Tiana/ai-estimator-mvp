from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from normalization import cell_text, display_number


SECTION_CODE = "earthworks"
SECTION_TITLE = "Земляные работы"

LAYOUT_MODEL = {
    "white_zone": {
        "columns": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
        "purpose": "visible estimate area",
    },
    "calc_zone": {
        "columns": ["J", "K", "L", "M", "N", "O"],
        "purpose": "row calculation area",
    },
    "helper_zone": {
        "columns": ["P", "Q", "R", "S", "T", "U", "V"],
        "purpose": "row-level control fields",
    },
}

SUPPORTED_FORMULA_TYPES = [
    "ref",
    "multiply",
    "sum",
    "ceil_divide",
    "roundup_to_step",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dump_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt(value: Any) -> str:
    if value is None:
        return "missing"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return display_number(value)
    return str(value)


def _formula_operand(value: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {"ref": value}


def _formula_ref(value: str | dict[str, Any]) -> dict[str, Any]:
    return {"type": "ref", "operand": _formula_operand(value)}


def _formula_multiply(*values: str | dict[str, Any]) -> dict[str, Any]:
    return {"type": "multiply", "operands": [_formula_operand(value) for value in values]}


def _formula_sum(*values: str | dict[str, Any]) -> dict[str, Any]:
    return {"type": "sum", "operands": [_formula_operand(value) for value in values]}


def _formula_ceil_divide(numerator: str | dict[str, Any], denominator: str | dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "ceil_divide",
        "operands": [_formula_operand(numerator), _formula_operand(denominator)],
    }


def _formula_roundup_to_step(value_ref: str | dict[str, Any], step_ref: str | dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "roundup_to_step",
        "value_ref": _formula_operand(value_ref),
        "step_ref": _formula_operand(step_ref),
    }


def _lineage_index(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fields = report.get("fields", [])
    return {cell_text(row.get("input_path")): row for row in fields if cell_text(row.get("input_path"))}


def _lineage_entry(
    lineage: dict[str, dict[str, Any]],
    input_path: str,
    *,
    fallback_source_type: str,
    fallback_source_path: str,
    fallback_source_note: str,
    warnings: list[str],
    required: bool = True,
) -> dict[str, Any]:
    row = lineage.get(input_path)
    if row is None:
        if required:
            warnings.append(f"missing lineage entry for {input_path}")
        return {
            "source_type": fallback_source_type,
            "source_path": fallback_source_path,
            "source_note": fallback_source_note,
            "trace_status": "untraced",
        }

    return {
        "source_type": row.get("source_type", fallback_source_type),
        "source_path": row.get("source_path", fallback_source_path),
        "source_note": row.get("source_note", fallback_source_note),
        "trace_status": row.get("status", "traced"),
    }


def _price_lineage(
    lineage: dict[str, dict[str, Any]],
    calc_price_key: str,
    warnings: list[str],
) -> dict[str, Any]:
    path = "consumables_amount" if calc_price_key == "consumables_amount" else f"internal_prices.{calc_price_key}"
    return _lineage_entry(
        lineage,
        path,
        fallback_source_type="normalized.prices by calc_price_key",
        fallback_source_path=f"prices[calc_price_key={calc_price_key}]",
        fallback_source_note="price traced from review sheet 02 by calc_price_key",
        warnings=warnings,
    )


def _make_calc_cell(
    target_col_role: str,
    value: Any,
    *,
    source_type: str = "",
    source_path: str = "",
    source_note: str = "",
    formula_model: dict[str, Any] | None = None,
    price_key: str | None = None,
    selected_price_source: str = "",
    effective_price_source: str = "",
    price_registry_code: str = "",
    fallback_key: str = "",
    excel_formula_exportable: bool | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    cell: dict[str, Any] = {
        "target_col_role": target_col_role,
        "value": value,
    }
    if source_type:
        cell["source_type"] = source_type
    if source_path:
        cell["source_path"] = source_path
    if source_note:
        cell["source_note"] = source_note
    if formula_model is not None:
        cell["formula_model"] = formula_model
    if price_key is not None:
        cell["price_key"] = price_key
    if selected_price_source:
        cell["selected_price_source"] = selected_price_source
    if effective_price_source:
        cell["effective_price_source"] = effective_price_source
    if price_registry_code:
        cell["price_registry_code"] = price_registry_code
    if fallback_key:
        cell["fallback_key"] = fallback_key
    if excel_formula_exportable is not None:
        cell["excel_formula_exportable"] = excel_formula_exportable
    if reason:
        cell["reason"] = reason
    return cell


def _make_white_zone() -> dict[str, Any]:
    return {
        "line_name": {"target_col_role": "B", "source": "estimate_line"},
        "unit": {"target_col_role": "C", "source": "unit"},
        "quantity": {"target_col_role": "D", "mirror_of": "calc_zone.quantity"},
        "material_unit_price": {"target_col_role": "E", "mirror_of": "calc_zone.material_unit_price"},
        "material_total": {"target_col_role": "F", "mirror_of": "calc_zone.material_total"},
        "work_unit_price": {"target_col_role": "G", "mirror_of": "calc_zone.work_unit_price"},
        "work_total": {"target_col_role": "H", "mirror_of": "calc_zone.work_total"},
        "row_total": {"target_col_role": "I", "mirror_of": "calc_zone.row_total"},
    }


def _helper_cell(
    helper_id: str,
    target_col_role: str,
    label: str,
    value: Any,
    *,
    source_type: str,
    source_path: str,
    source_note: str,
    formula_model: dict[str, Any] | None = None,
    excel_formula_exportable: bool | None = None,
    reason: str | None = None,
    trace_status: str = "traced",
) -> dict[str, Any]:
    cell: dict[str, Any] = {
        "helper_id": helper_id,
        "target_col_role": target_col_role,
        "label": label,
        "value": value,
        "source_type": source_type,
        "source_path": source_path,
        "source_note": source_note,
        "trace_status": trace_status,
    }
    if formula_model is not None:
        cell["formula_model"] = formula_model
    if excel_formula_exportable is not None:
        cell["excel_formula_exportable"] = excel_formula_exportable
    if reason:
        cell["reason"] = reason
    return cell


def _estimate_line_by_code(result_lines: list[dict[str, Any]], code: str, errors: list[str]) -> dict[str, Any] | None:
    for line in result_lines:
        if cell_text(line.get("code")) == code:
            return line
    errors.append(f"missing result line: {code}")
    return None


def _build_row(
    *,
    code: str,
    estimate_line: str,
    unit: str,
    quantity_value: Any,
    quantity_formula_model: dict[str, Any],
    quantity_source_type: str,
    quantity_source_path: str,
    quantity_source_note: str,
    material_unit_price_value: Any,
    material_unit_price_key: str | None,
    material_unit_price_source: dict[str, Any] | None,
    material_total_value: Any,
    work_unit_price_value: Any,
    work_unit_price_key: str | None,
    work_unit_price_source: dict[str, Any] | None,
    work_total_value: Any,
    helper_cells: list[dict[str, Any]],
    row_total_value: Any,
) -> dict[str, Any]:
    calc_zone = {
        "quantity": _make_calc_cell(
            "J",
            quantity_value,
            source_type=quantity_source_type,
            source_path=quantity_source_path,
            source_note=quantity_source_note,
            formula_model=quantity_formula_model,
        ),
        "material_unit_price": _make_calc_cell(
            "K",
            material_unit_price_value,
            source_type=(material_unit_price_source or {}).get("source_type", "literal_zero" if not material_unit_price_key else "normalized.prices by calc_price_key"),
            source_path=(material_unit_price_source or {}).get(
                "source_path",
                "literal_zero" if not material_unit_price_key else f"internal_prices.{material_unit_price_key}",
            ),
            source_note=(material_unit_price_source or {}).get("source_note", ""),
            price_key=material_unit_price_key,
            selected_price_source=(material_unit_price_source or {}).get("selected_price_source", ""),
            effective_price_source=(material_unit_price_source or {}).get("effective_price_source", ""),
            price_registry_code=(material_unit_price_source or {}).get("price_registry_code", ""),
            fallback_key=(material_unit_price_source or {}).get("fallback_key", ""),
        ),
        "material_total": _make_calc_cell(
            "L",
            material_total_value,
            formula_model=_formula_multiply("calc_zone.quantity", "calc_zone.material_unit_price"),
            source_type="calculator_result",
            source_path=f"estimate_lines[code={code}].material_total",
            source_note="formula-ready material total",
        ),
        "work_unit_price": _make_calc_cell(
            "M",
            work_unit_price_value,
            source_type=(work_unit_price_source or {}).get("source_type", "literal_zero" if not work_unit_price_key else "normalized.prices by calc_price_key"),
            source_path=(work_unit_price_source or {}).get(
                "source_path",
                "literal_zero" if not work_unit_price_key else f"internal_prices.{work_unit_price_key}",
            ),
            source_note=(work_unit_price_source or {}).get("source_note", ""),
            price_key=work_unit_price_key,
            selected_price_source=(work_unit_price_source or {}).get("selected_price_source", ""),
            effective_price_source=(work_unit_price_source or {}).get("effective_price_source", ""),
            price_registry_code=(work_unit_price_source or {}).get("price_registry_code", ""),
            fallback_key=(work_unit_price_source or {}).get("fallback_key", ""),
        ),
        "work_total": _make_calc_cell(
            "N",
            work_total_value,
            formula_model=_formula_multiply("calc_zone.quantity", "calc_zone.work_unit_price"),
            source_type="calculator_result",
            source_path=f"estimate_lines[code={code}].work_total",
            source_note="formula-ready work total",
        ),
        "row_total": _make_calc_cell(
            "O",
            row_total_value,
            formula_model=_formula_sum("calc_zone.material_total", "calc_zone.work_total"),
            source_type="calculator_result",
            source_path=f"estimate_lines[code={code}].line_total",
            source_note="formula-ready row total",
        ),
    }

    white_zone = _make_white_zone()
    return {
        "row_id": f"earthworks.{code}",
        "estimate_line": estimate_line,
        "unit": unit,
        "white_zone": white_zone,
        "calc_zone": calc_zone,
        "helper_zone": {"cells": helper_cells},
        "excel_export_hints": {
            "white_zone_mirrors_calc_zone": True,
            "helper_cells_are_row_level": True,
            "formula_models_symbolic": True,
            "no_named_ranges_required": True,
        },
    }


def _build_formula_ready(
    calculator_input: dict[str, Any],
    calculation_result: dict[str, Any],
    lineage_report: dict[str, Any],
) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []
    lineage = _lineage_index(lineage_report)
    result_lines = calculation_result.get("estimate_lines", []) or []
    volume_result = calculation_result.get("volume_result", {}) or {}
    project_quantities = {
        key: calculator_input.get(key)
        for key in (
            "pit_area_m2",
            "pit_excavation_depth_m",
            "sand_base_volume_m3",
            "trench_volume_m3",
            "geotextile_area_m2",
            "geotextile_laying_area_m2",
            "communications_length_m",
        )
    }
    defaults = {
        key: calculator_input.get(key)
        for key in (
            "excavator_productivity_m3_per_shift",
            "manual_refinement_depth_m",
            "trench_width_m",
            "sand_compaction_coeff",
            "sand_truck_step_m3",
            "geotextile_overlap_coeff",
            "geotextile_roll_area_m2",
            "axis_marking_shifts",
        )
    }

    def traced_source(
        input_path: str,
        *,
        fallback_source_type: str,
        fallback_source_path: str,
        fallback_source_note: str,
        required: bool = True,
    ) -> dict[str, Any]:
        return _lineage_entry(
            lineage,
            input_path,
            fallback_source_type=fallback_source_type,
            fallback_source_path=fallback_source_path,
            fallback_source_note=fallback_source_note,
            warnings=warnings,
            required=required,
        )

    def price_source(calc_price_key: str) -> dict[str, Any]:
        return _price_lineage(lineage, calc_price_key, warnings)

    def missing_row(code: str, unit: str = "") -> dict[str, Any]:
        placeholder_note = "missing calculator result line"
        return {
            "row_id": f"earthworks.{code}",
            "estimate_line": code,
            "unit": unit,
            "white_zone": _make_white_zone(),
            "calc_zone": {
                "quantity": _make_calc_cell("J", None, source_type="missing_result_line", source_path=f"estimate_lines[code={code}]", source_note=placeholder_note),
                "material_unit_price": _make_calc_cell("K", None, source_type="missing_result_line", source_path=f"estimate_lines[code={code}]", source_note=placeholder_note),
                "material_total": _make_calc_cell("L", None, source_type="missing_result_line", source_path=f"estimate_lines[code={code}]", source_note=placeholder_note),
                "work_unit_price": _make_calc_cell("M", None, source_type="missing_result_line", source_path=f"estimate_lines[code={code}]", source_note=placeholder_note),
                "work_total": _make_calc_cell("N", None, source_type="missing_result_line", source_path=f"estimate_lines[code={code}]", source_note=placeholder_note),
                "row_total": _make_calc_cell("O", None, source_type="missing_result_line", source_path=f"estimate_lines[code={code}]", source_note=placeholder_note),
            },
            "helper_zone": {"cells": []},
            "excel_export_hints": {
                "white_zone_mirrors_calc_zone": True,
                "helper_cells_are_row_level": True,
                "formula_models_symbolic": True,
                "no_named_ranges_required": True,
            },
            "status": "missing_result_line",
            "reason": placeholder_note,
        }

    def axis_marking_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "axis_marking", errors)
        if line is None:
            return missing_row("axis_marking", "смена")
        axis_source = traced_source(
            "axis_marking_shifts",
            fallback_source_type="GENERIC_CALCULATOR_DEFAULTS",
            fallback_source_path="GENERIC_CALCULATOR_DEFAULTS.axis_marking_shifts",
            fallback_source_note="default shift count for axis marking",
        )
        quantity_value = _number(line.get("quantity"))
        helper_cells = [
            _helper_cell(
                "axis_marking_shifts",
                "P",
                "Смены выноса осей",
                calculator_input.get("axis_marking_shifts"),
                source_type=axis_source["source_type"],
                source_path=axis_source["source_path"],
                source_note=axis_source["source_note"],
            )
        ]
        return _build_row(
            code="axis_marking",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=quantity_value,
            quantity_formula_model=_formula_ref("helper_zone.axis_marking_shifts"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.axis_marking_shifts",
            quantity_source_note="row quantity mirrors helper shift count",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key=None,
            material_unit_price_source=None,
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key="axis_marking_work_unit_price",
            work_unit_price_source=price_source("axis_marking_work_unit_price"),
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helper_cells,
            row_total_value=_number(line.get("line_total")),
        )

    def excavator_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "excavator_jcb", errors)
        if line is None:
            return missing_row("excavator_jcb", "смена")
        pit_area_source = traced_source(
            "pit_area_m2",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.pit_area_m2.value",
            fallback_source_note="project pit area",
        )
        pit_depth_source = traced_source(
            "pit_excavation_depth_m",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.pit_excavation_depth_m.value",
            fallback_source_note="project excavation depth",
        )
        productivity_source = traced_source(
            "excavator_productivity_m3_per_shift",
            fallback_source_type="GENERIC_CALCULATOR_DEFAULTS",
            fallback_source_path="GENERIC_CALCULATOR_DEFAULTS.excavator_productivity_m3_per_shift",
            fallback_source_note="generic excavator productivity",
        )
        volume_value = _number(volume_result.get("machine_excavation_volume_m3"))
        shifts_value = _number(line.get("quantity"))
        helper_cells = [
            _helper_cell(
                "pit_area_m2",
                "P",
                "Площадь котлована",
                calculator_input.get("pit_area_m2"),
                source_type=pit_area_source["source_type"],
                source_path=pit_area_source["source_path"],
                source_note=pit_area_source["source_note"],
            ),
            _helper_cell(
                "pit_excavation_depth_m",
                "Q",
                "Глубина механизированной выемки",
                calculator_input.get("pit_excavation_depth_m"),
                source_type=pit_depth_source["source_type"],
                source_path=pit_depth_source["source_path"],
                source_note=pit_depth_source["source_note"],
            ),
            _helper_cell(
                "machine_excavation_volume_m3",
                "R",
                "Объем механизированной выемки",
                volume_value,
                source_type="derived_from_normalized_details",
                source_path="parameters.pit_area_m2.value * parameters.pit_excavation_depth_m.value",
                source_note="derived excavation volume for excavator shifts",
                formula_model=_formula_multiply("helper_zone.pit_area_m2", "helper_zone.pit_excavation_depth_m"),
            ),
            _helper_cell(
                "excavator_productivity_m3_per_shift",
                "S",
                "Производительность экскаватора",
                calculator_input.get("excavator_productivity_m3_per_shift"),
                source_type=productivity_source["source_type"],
                source_path=productivity_source["source_path"],
                source_note=productivity_source["source_note"],
            ),
            _helper_cell(
                "excavator_shifts",
                "T",
                "Смены экскаватора",
                shifts_value,
                source_type="calculator_result",
                source_path="volume_result.excavator_shifts",
                source_note="ceil(machine_excavation_volume_m3 / productivity)",
                formula_model=_formula_ceil_divide("helper_zone.machine_excavation_volume_m3", "helper_zone.excavator_productivity_m3_per_shift"),
            ),
        ]
        return _build_row(
            code="excavator_jcb",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=shifts_value,
            quantity_formula_model=_formula_ref("helper_zone.excavator_shifts"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.excavator_shifts",
            quantity_source_note="row quantity mirrors helper shift count",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key="excavator_material_unit_price",
            material_unit_price_source=price_source("excavator_material_unit_price"),
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key="excavator_work_unit_price",
            work_unit_price_source=price_source("excavator_work_unit_price"),
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helper_cells,
            row_total_value=_number(line.get("line_total")),
        )

    def manual_excavation_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "manual_excavation", errors)
        if line is None:
            return missing_row("manual_excavation", "м3")
        pit_area_source = traced_source(
            "pit_area_m2",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.pit_area_m2.value",
            fallback_source_note="project pit area",
        )
        manual_depth_source = traced_source(
            "manual_refinement_depth_m",
            fallback_source_type="GENERIC_CALCULATOR_DEFAULTS",
            fallback_source_path="GENERIC_CALCULATOR_DEFAULTS.manual_refinement_depth_m",
            fallback_source_note="generic manual refinement depth",
        )
        trench_volume_source = traced_source(
            "trench_volume_m3",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.trench_volume_m3.value",
            fallback_source_note="project trench volume",
        )
        manual_total_value = _number(volume_result.get("manual_excavation_total_m3"))
        helper_cells = [
            _helper_cell(
                "pit_area_m2",
                "P",
                "Площадь котлована",
                calculator_input.get("pit_area_m2"),
                source_type=pit_area_source["source_type"],
                source_path=pit_area_source["source_path"],
                source_note=pit_area_source["source_note"],
            ),
            _helper_cell(
                "manual_refinement_depth_m",
                "Q",
                "Глубина ручной доработки",
                calculator_input.get("manual_refinement_depth_m"),
                source_type=manual_depth_source["source_type"],
                source_path=manual_depth_source["source_path"],
                source_note=manual_depth_source["source_note"],
            ),
            _helper_cell(
                "manual_pit_volume_m3",
                "R",
                "Ручная доработка котлована",
                _number(volume_result.get("manual_pit_volume_m3")),
                source_type="derived_from_normalized_details",
                source_path="parameters.pit_area_m2.value * GENERIC_CALCULATOR_DEFAULTS.manual_refinement_depth_m",
                source_note="manual pit volume derived from project area and default depth",
                formula_model=_formula_multiply("helper_zone.pit_area_m2", "helper_zone.manual_refinement_depth_m"),
            ),
            _helper_cell(
                "trench_volume_m3",
                "S",
                "Объем траншей",
                calculator_input.get("trench_volume_m3"),
                source_type=trench_volume_source["source_type"],
                source_path=trench_volume_source["source_path"],
                source_note=trench_volume_source["source_note"],
            ),
            _helper_cell(
                "manual_excavation_total_m3",
                "T",
                "Итог ручной разработки",
                manual_total_value,
                source_type="derived_from_normalized_details",
                source_path="manual_pit_volume_m3 + trench_volume_m3",
                source_note="manual excavation total used by calculator",
                formula_model=_formula_sum("helper_zone.manual_pit_volume_m3", "helper_zone.trench_volume_m3"),
            ),
        ]
        return _build_row(
            code="manual_excavation",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=_number(line.get("quantity")),
            quantity_formula_model=_formula_ref("helper_zone.manual_excavation_total_m3"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.manual_excavation_total_m3",
            quantity_source_note="row quantity mirrors helper total",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key=None,
            material_unit_price_source=None,
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key="manual_excavation_work_unit_price",
            work_unit_price_source=price_source("manual_excavation_work_unit_price"),
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helper_cells,
            row_total_value=_number(line.get("line_total")),
        )

    def geotextile_laying_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "geotextile_laying", errors)
        if line is None:
            return missing_row("geotextile_laying", "м2")
        laying_source = traced_source(
            "geotextile_laying_area_m2",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.geotextile_laying_area_m2.value",
            fallback_source_note="project geotextile laying area",
        )
        helper_cells = [
            _helper_cell(
                "geotextile_laying_area_m2",
                "P",
                "Площадь укладки геотекстиля",
                calculator_input.get("geotextile_laying_area_m2"),
                source_type=laying_source["source_type"],
                source_path=laying_source["source_path"],
                source_note=laying_source["source_note"],
            )
        ]
        return _build_row(
            code="geotextile_laying",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=_number(line.get("quantity")),
            quantity_formula_model=_formula_ref("helper_zone.geotextile_laying_area_m2"),
            quantity_source_type="normalized.project_parameters",
            quantity_source_path="parameters.geotextile_laying_area_m2.value",
            quantity_source_note="layout mirrors the review workbook project parameter",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key=None,
            material_unit_price_source=None,
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key="geotextile_laying_work_unit_price",
            work_unit_price_source=price_source("geotextile_laying_work_unit_price"),
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helper_cells,
            row_total_value=_number(line.get("line_total")),
        )

    def geotextile_material_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "geotextile_material", errors)
        if line is None:
            return missing_row("geotextile_material", "м2")
        area_source = traced_source(
            "geotextile_area_m2",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.geotextile_area_m2.value",
            fallback_source_note="project geotextile area",
        )
        overlap_source = traced_source(
            "geotextile_overlap_coeff",
            fallback_source_type="GENERIC_CALCULATOR_DEFAULTS",
            fallback_source_path="GENERIC_CALCULATOR_DEFAULTS.geotextile_overlap_coeff",
            fallback_source_note="generic overlap coefficient",
        )
        roll_area_source = traced_source(
            "geotextile_roll_area_m2",
            fallback_source_type="GENERIC_CALCULATOR_DEFAULTS",
            fallback_source_path="GENERIC_CALCULATOR_DEFAULTS.geotextile_roll_area_m2",
            fallback_source_note="generic roll area",
        )
        with_overlap_value = _number(volume_result.get("geotextile_with_overlap_m2"))
        rolls_value = _number(volume_result.get("geotextile_rolls"))
        quantity_value = _number(line.get("quantity"))
        helper_cells = [
            _helper_cell(
                "geotextile_area_m2",
                "P",
                "Площадь геотекстиля",
                calculator_input.get("geotextile_area_m2"),
                source_type=area_source["source_type"],
                source_path=area_source["source_path"],
                source_note=area_source["source_note"],
            ),
            _helper_cell(
                "geotextile_overlap_coeff",
                "Q",
                "Коэффициент нахлёста",
                calculator_input.get("geotextile_overlap_coeff"),
                source_type=overlap_source["source_type"],
                source_path=overlap_source["source_path"],
                source_note=overlap_source["source_note"],
            ),
            _helper_cell(
                "geotextile_with_overlap_m2",
                "R",
                "Площадь с нахлёстом",
                with_overlap_value,
                source_type="derived_from_normalized_details",
                source_path="parameters.geotextile_area_m2.value * GENERIC_CALCULATOR_DEFAULTS.geotextile_overlap_coeff",
                source_note="geotextile area after overlap",
                formula_model=_formula_multiply("helper_zone.geotextile_area_m2", "helper_zone.geotextile_overlap_coeff"),
            ),
            _helper_cell(
                "geotextile_roll_area_m2",
                "S",
                "Площадь рулона",
                calculator_input.get("geotextile_roll_area_m2"),
                source_type=roll_area_source["source_type"],
                source_path=roll_area_source["source_path"],
                source_note=roll_area_source["source_note"],
            ),
            _helper_cell(
                "geotextile_rolls",
                "T",
                "Рулоны геотекстиля",
                rolls_value,
                source_type="derived_from_normalized_details",
                source_path="geotextile_with_overlap_m2 / geotextile_roll_area_m2",
                source_note="ceil(area with overlap / roll area)",
                formula_model=_formula_ceil_divide("helper_zone.geotextile_with_overlap_m2", "helper_zone.geotextile_roll_area_m2"),
            ),
            _helper_cell(
                "geotextile_material_quantity_m2",
                "U",
                "Материальная единица геотекстиля",
                quantity_value,
                source_type="derived_from_normalized_details",
                source_path="geotextile_rolls * geotextile_roll_area_m2",
                source_note="material quantity used by calculator",
                formula_model=_formula_multiply("helper_zone.geotextile_rolls", "helper_zone.geotextile_roll_area_m2"),
            ),
        ]
        return _build_row(
            code="geotextile_material",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=quantity_value,
            quantity_formula_model=_formula_ref("helper_zone.geotextile_material_quantity_m2"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.geotextile_material_quantity_m2",
            quantity_source_note="row quantity mirrors helper quantity",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key="geotextile_material_unit_price",
            material_unit_price_source=price_source("geotextile_material_unit_price"),
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key=None,
            work_unit_price_source=None,
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helper_cells,
            row_total_value=_number(line.get("line_total")),
        )

    def sand_helper_cells() -> list[dict[str, Any]]:
        sand_base_source = traced_source(
            "sand_base_volume_m3",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.sand_base_volume_m3.value",
            fallback_source_note="project sand base volume",
        )
        trench_volume_source = traced_source(
            "trench_volume_m3",
            fallback_source_type="normalized.project_parameters",
            fallback_source_path="parameters.trench_volume_m3.value",
            fallback_source_note="project trench volume",
        )
        compaction_source = traced_source(
            "sand_compaction_coeff",
            fallback_source_type="GENERIC_CALCULATOR_DEFAULTS",
            fallback_source_path="GENERIC_CALCULATOR_DEFAULTS.sand_compaction_coeff",
            fallback_source_note="generic sand compaction coefficient",
        )
        step_source = traced_source(
            "sand_truck_step_m3",
            fallback_source_type="GENERIC_CALCULATOR_DEFAULTS",
            fallback_source_path="GENERIC_CALCULATOR_DEFAULTS.sand_truck_step_m3",
            fallback_source_note="generic truck step",
        )
        total_value = _number(volume_result.get("sand_total_m3"))
        order_value = _number(volume_result.get("sand_order_volume_m3"))
        return [
            _helper_cell(
                "sand_base_volume_m3",
                "P",
                "Песок по проекту",
                calculator_input.get("sand_base_volume_m3"),
                source_type=sand_base_source["source_type"],
                source_path=sand_base_source["source_path"],
                source_note=sand_base_source["source_note"],
            ),
            _helper_cell(
                "sand_compaction_coeff",
                "Q",
                "Коэффициент уплотнения",
                calculator_input.get("sand_compaction_coeff"),
                source_type=compaction_source["source_type"],
                source_path=compaction_source["source_path"],
                source_note=compaction_source["source_note"],
            ),
            _helper_cell(
                "trench_volume_m3",
                "R",
                "Объем траншей",
                calculator_input.get("trench_volume_m3"),
                source_type=trench_volume_source["source_type"],
                source_path=trench_volume_source["source_path"],
                source_note=trench_volume_source["source_note"],
            ),
            _helper_cell(
                "sand_total_m3",
                "S",
                "Расчетный объем песка",
                total_value,
                source_type="derived_from_normalized_details",
                source_path="sand_base_volume_m3 * sand_compaction_coeff + trench_volume_m3 * sand_compaction_coeff",
                source_note="sum of compacted base and trench sand",
                formula_model=_formula_sum(
                    _formula_multiply("helper_zone.sand_base_volume_m3", "helper_zone.sand_compaction_coeff"),
                    _formula_multiply("helper_zone.trench_volume_m3", "helper_zone.sand_compaction_coeff"),
                ),
            ),
            _helper_cell(
                "sand_truck_step_m3",
                "T",
                "Шаг машины",
                calculator_input.get("sand_truck_step_m3"),
                source_type=step_source["source_type"],
                source_path=step_source["source_path"],
                source_note=step_source["source_note"],
            ),
            _helper_cell(
                "sand_order_volume_m3",
                "U",
                "Заказной объем песка",
                order_value,
                source_type="derived_from_normalized_details",
                source_path="roundup_to_step(sand_total_m3, sand_truck_step_m3)",
                source_note="ordered sand volume rounded up to truck step",
                formula_model=_formula_roundup_to_step("helper_zone.sand_total_m3", "helper_zone.sand_truck_step_m3"),
            ),
        ]

    def sand_filling_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "sand_filling", errors)
        if line is None:
            return missing_row("sand_filling", "м3")
        helpers = sand_helper_cells()
        return _build_row(
            code="sand_filling",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=_number(line.get("quantity")),
            quantity_formula_model=_formula_ref("helper_zone.sand_order_volume_m3"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.sand_order_volume_m3",
            quantity_source_note="row quantity mirrors helper ordered volume",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key=None,
            material_unit_price_source=None,
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key="sand_filling_work_unit_price",
            work_unit_price_source=price_source("sand_filling_work_unit_price"),
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helpers,
            row_total_value=_number(line.get("line_total")),
        )

    def sand_material_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "sand_material", errors)
        if line is None:
            return missing_row("sand_material", "м3")
        helpers = sand_helper_cells()
        return _build_row(
            code="sand_material",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=_number(line.get("quantity")),
            quantity_formula_model=_formula_ref("helper_zone.sand_order_volume_m3"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.sand_order_volume_m3",
            quantity_source_note="row quantity mirrors helper ordered volume",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key="sand_material_unit_price",
            material_unit_price_source=price_source("sand_material_unit_price"),
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key=None,
            work_unit_price_source=None,
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helpers,
            row_total_value=_number(line.get("line_total")),
        )

    def sand_manual_moving_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "sand_manual_moving", errors)
        if line is None:
            return missing_row("sand_manual_moving", "м3")
        helpers = sand_helper_cells()
        return _build_row(
            code="sand_manual_moving",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=_number(line.get("quantity")),
            quantity_formula_model=_formula_ref("helper_zone.sand_order_volume_m3"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.sand_order_volume_m3",
            quantity_source_note="row quantity mirrors helper ordered volume",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key=None,
            material_unit_price_source=None,
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key="sand_manual_moving_work_unit_price",
            work_unit_price_source=price_source("sand_manual_moving_work_unit_price"),
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helpers,
            row_total_value=_number(line.get("line_total")),
        )

    def communications_row(code: str) -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, code, errors)
        if line is None:
            return missing_row(code, "мп")
        communications_source = traced_source(
            "communications_length_m",
            fallback_source_type="derived_from_normalized_details",
            fallback_source_path="details.communications_pipe_items[*].total_length_m",
            fallback_source_note="communications total length from included pipe rows",
        )
        pipe_items = calculator_input.get("communications_pipe_items", []) or []
        included_count = sum(1 for item in pipe_items if item.get("include_in_communications", item.get("included", True)))
        helpers = [
            _helper_cell(
                "communications_pipe_items_count",
                "P",
                "Включенные позиции труб",
                included_count,
                source_type="normalized.details.communications_pipe_items",
                source_path="details.communications_pipe_items",
                source_note="count of included communications pipe rows",
            ),
            _helper_cell(
                "communications_total_length_m",
                "Q",
                "Суммарная длина коммуникаций",
                _number(volume_result.get("communications_length_m")),
                source_type=communications_source["source_type"],
                source_path=communications_source["source_path"],
                source_note=communications_source["source_note"],
                formula_model=_formula_ref("calculator_result.volume_result.communications_length_m"),
                excel_formula_exportable=False,
                reason="value comes from calculator result / derived details",
            ),
            _helper_cell(
                "communications_length_calc_method",
                "R",
                "Метод расчета длины",
                calculator_input.get("communications_length_calc_method"),
                source_type="GENERIC_CALCULATOR_DEFAULTS",
                source_path="GENERIC_CALCULATOR_DEFAULTS.communications_length_calc_method",
                source_note="generic communications length method",
            ),
        ]
        return _build_row(
            code=code,
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=_number(line.get("quantity")),
            quantity_formula_model=_formula_ref("helper_zone.communications_total_length_m"),
            quantity_source_type="derived_from_normalized_details",
            quantity_source_path="helper_zone.communications_total_length_m",
            quantity_source_note="row quantity mirrors communications total helper",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key="communications_material_unit_price" if code == "communications_material" else None,
            material_unit_price_source=price_source("communications_material_unit_price") if code == "communications_material" else None,
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key="communications_work_unit_price" if code == "communications_work" else None,
            work_unit_price_source=price_source("communications_work_unit_price") if code == "communications_work" else None,
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helpers,
            row_total_value=_number(line.get("line_total")),
        )

    def consumables_row() -> dict[str, Any]:
        line = _estimate_line_by_code(result_lines, "consumables", errors)
        if line is None:
            return missing_row("consumables", "комплект")
        consumables_source = price_source("consumables_amount")
        helper_cells = [
            _helper_cell(
                "consumables_quantity",
                "P",
                "Количество комплекта",
                1,
                source_type="literal_system_metadata",
                source_path="literal_quantity_1",
                source_note="fixed consumables line quantity",
            ),
            _helper_cell(
                "calc_price_key",
                "Q",
                "Ключ цены",
                "consumables_amount",
                source_type=consumables_source["source_type"],
                source_path=consumables_source["source_path"],
                source_note=consumables_source["source_note"],
            ),
            _helper_cell(
                "consumables_amount",
                "R",
                "Фиксированная сумма",
                calculator_input.get("consumables_amount"),
                source_type=consumables_source["source_type"],
                source_path=consumables_source["source_path"],
                source_note=consumables_source["source_note"],
            ),
        ]
        return _build_row(
            code="consumables",
            estimate_line=line["name"],
            unit=line["unit"],
            quantity_value=_number(line.get("quantity")),
            quantity_formula_model=_formula_ref("helper_zone.consumables_quantity"),
            quantity_source_type="literal_system_metadata",
            quantity_source_path="literal_quantity_1",
            quantity_source_note="fixed consumables quantity",
            material_unit_price_value=_number(line.get("material_unit_price")) or 0.0,
            material_unit_price_key="consumables_amount",
            material_unit_price_source=consumables_source,
            material_total_value=_number(line.get("material_total")) or 0.0,
            work_unit_price_value=_number(line.get("work_unit_price")) or 0.0,
            work_unit_price_key=None,
            work_unit_price_source=None,
            work_total_value=_number(line.get("work_total")) or 0.0,
            helper_cells=helper_cells,
            row_total_value=_number(line.get("line_total")),
        )

    rows = [
        axis_marking_row(),
        excavator_row(),
        manual_excavation_row(),
        geotextile_laying_row(),
        geotextile_material_row(),
        sand_filling_row(),
        sand_material_row(),
        sand_manual_moving_row(),
        communications_row("communications_work"),
        communications_row("communications_material"),
        consumables_row(),
    ]

    rows_with_formula_model = sum(1 for row in rows if row["calc_zone"]["row_total"].get("formula_model"))
    rows_with_control_fields = sum(1 for row in rows if row["helper_zone"].get("cells"))
    helper_cells_count = sum(len(row["helper_zone"].get("cells", [])) for row in rows)
    row_count_note = f"formula-ready row count: {len(rows)}"
    excel_export_ready = bool(rows) and all(row["calc_zone"]["row_total"].get("formula_model") for row in rows) and not errors

    summary = {
        "excel_export_ready": excel_export_ready,
        "rows": len(rows),
        "rows_with_formula_model": rows_with_formula_model,
        "rows_with_control_fields": rows_with_control_fields,
        "layout_model_present": True,
        "row_count_note": row_count_note,
        "warnings": warnings,
        "errors": errors,
    }

    return {
        "section_code": SECTION_CODE,
        "section_title": SECTION_TITLE,
        "excel_export_ready": excel_export_ready,
        "layout_model": LAYOUT_MODEL,
        "supported_formula_types": SUPPORTED_FORMULA_TYPES,
        "source_files": {
            "calculator_input": None,
            "calculation_result": None,
            "lineage_report": None,
        },
        "rows": rows,
        "summary": summary,
        "row_count_note": row_count_note,
        "excel_export_hints": {
            "white_zone_mirrors_calc_zone": True,
            "helper_cells_are_row_level": True,
            "formula_models_symbolic": True,
            "no_named_ranges_required": True,
        },
        "warnings": warnings,
        "errors": errors,
        "rows_with_formula_model": rows_with_formula_model,
        "rows_with_control_fields": rows_with_control_fields,
        "helper_cells_count": helper_cells_count,
    }


def _render_report(formula_ready: dict[str, Any], calculator_input_path: str, calculation_result_path: str, lineage_report_path: str) -> str:
    rows = formula_ready.get("rows", [])
    lines = [
        "# Formula-ready result report",
        "",
        "## Verdict",
        f"- excel_export_ready: {'yes' if formula_ready.get('excel_export_ready') else 'no'}",
        f"- rows: {len(rows)}",
        f"- rows_with_formula_model: {formula_ready.get('rows_with_formula_model', 0)}",
        f"- rows_with_control_fields: {formula_ready.get('rows_with_control_fields', 0)}",
        f"- layout_model_present: {'yes' if formula_ready.get('layout_model') else 'no'}",
        f"- row_count_note: {formula_ready.get('row_count_note', 'missing')}",
        f"- warnings: {len(formula_ready.get('warnings', []) or [])}",
        f"- errors: {len(formula_ready.get('errors', []) or [])}",
        "",
        "## Purpose",
        "This output is prepared for future Excel export with formulas.",
        "",
        "## Important",
        "Formula models are symbolic.",
        "Excel cell references will be generated later by Excel exporter.",
        "Supported symbolic formula types: ref, multiply, sum, ceil_divide, roundup_to_step.",
        "",
        "## Source",
        f"- calculator_input: {calculator_input_path}",
        f"- calculation_result: {calculation_result_path}",
        f"- lineage_report: {lineage_report_path}",
        "",
        "## Layout model",
        "- white_zone: A:I",
        "- calc_zone: J:O",
        "- helper_zone: P:V",
        "",
        "## Supported formula types",
    ]
    lines.extend(f"- {formula_type}" for formula_type in formula_ready.get("supported_formula_types", []) or [])
    lines.extend(
        [
            "",
            "## Errors",
        ]
    )
    errors_list = formula_ready.get("errors", []) or []
    if errors_list:
        lines.extend(f"- {error}" for error in errors_list)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Rows summary",
            "",
            "| row_id | estimate_line | quantity | material_price | work_price | total | formula_ready | helper_cells |",
            "|---|---|---:|---:|---:|---:|---|---:|",
        ]
    )

    for row in rows:
        calc_zone = row["calc_zone"]
        quantity = _fmt(calc_zone["quantity"]["value"])
        material_price = _fmt(calc_zone["material_unit_price"]["value"])
        work_price = _fmt(calc_zone["work_unit_price"]["value"])
        total = _fmt(calc_zone["row_total"]["value"])
        formula_ready_flag = "yes" if calc_zone["row_total"].get("formula_model") else "no"
        helper_cells = len(row.get("helper_zone", {}).get("cells", []))
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["estimate_line"],
                    quantity,
                    material_price,
                    work_price,
                    total,
                    formula_ready_flag,
                    str(helper_cells),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Warnings",
        ]
    )
    warnings_list = formula_ready.get("warnings", []) or []
    if warnings_list:
        lines.extend(f"- {warning}" for warning in warnings_list)
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build formula-ready result for earthworks")
    parser.add_argument("--calculator-input", required=True, help="Path to earthworks_calculation_input.json")
    parser.add_argument(
        "--calculation-result",
        required=True,
        help="Path to calculation_result/result.json",
    )
    parser.add_argument("--lineage-report", required=True, help="Path to input_lineage_report.json")
    parser.add_argument("--out", required=True, help="Path for formula_ready_result.json")
    parser.add_argument("--report", required=True, help="Path for formula_ready_report.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    calculator_input_path = Path(args.calculator_input)
    calculation_result_path = Path(args.calculation_result)
    lineage_report_path = Path(args.lineage_report)
    out_path = Path(args.out)
    report_path = Path(args.report)

    calculator_input = load_json(calculator_input_path)
    calculation_result = load_json(calculation_result_path)
    lineage_report = load_json(lineage_report_path)

    formula_ready = _build_formula_ready(calculator_input, calculation_result, lineage_report)
    formula_ready["source_files"] = {
        "calculator_input": str(calculator_input_path),
        "calculation_result": str(calculation_result_path),
        "lineage_report": str(lineage_report_path),
    }

    dump_json(out_path, formula_ready)
    dump_text(
        report_path,
        _render_report(formula_ready, str(calculator_input_path), str(calculation_result_path), str(lineage_report_path)),
    )

    print(f"formula_ready_result: {out_path}")
    print(f"report: {report_path}")
    print(f"excel_export_ready: {'yes' if formula_ready.get('excel_export_ready') else 'no'}")
    print(f"rows: {len(formula_ready.get('rows', []))}")
    print(f"warnings: {len(formula_ready.get('warnings', []) or [])}")

    return 0 if formula_ready.get("excel_export_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
