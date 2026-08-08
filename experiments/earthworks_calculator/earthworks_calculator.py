from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Any


def _to_decimal(value: float | int | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _round_decimal(value: Decimal, places: str = "0.001") -> float:
    rounded = value.quantize(Decimal(places), rounding=ROUND_HALF_UP)
    return float(rounded)


def _require_positive(name: str, value: float | int | None) -> None:
    if value is None:
        raise ValueError(f"{name} is required")
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def _require_non_negative(name: str, value: float | int | None) -> None:
    if value is None:
        raise ValueError(f"{name} is required")
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0")


@dataclass(frozen=True)
class EarthworksInput:
    project_name: str
    pit_area_m2: float
    case_meta: dict[str, Any] = field(default_factory=dict)
    assumptions: dict[str, bool] = field(default_factory=dict)
    excavator_shifts_calc_method: str = "legacy_manual_shifts"
    pit_excavation_depth_m: float | None = None
    excavator_productivity_m3_per_shift: float = 80.0
    pit_items: list[dict[str, Any]] | None = None
    manual_excavation_calc_method: str = "legacy_manual_override"
    manual_refinement_depth_m: float = 0.08
    trench_volume_m3: float | None = None
    trench_length_m: float | None = None
    trench_depth_m: float | None = None
    trench_width_m: float | None = 0.4
    trench_routes: list[dict[str, Any]] | None = None
    # Manual hand-dig depth beyond the pit floor, by network type (2026-08-09, real formulas
    # confirmed in TRC/ЮСВ/АРК - see manual_trench_depth_by_network_type() docstring for the
    # full derivation). Defaults are the ТРЦ/ЮСВ average per matching network label; АРК had no
    # per-network breakdown at all (one flat 0.5m for everything), so its value is reused as the
    # fallback for any route whose network type can't be recognized from its name/route_code.
    # Elena, 2026-08-09: make these manual/reviewable per project, not hardcoded silently.
    manual_trench_depth_k1_m: float = 0.4
    manual_trench_depth_k2_m: float = 0.6
    manual_trench_depth_water_m: float = 1.6
    manual_trench_depth_eo_m: float = 0.65
    manual_trench_depth_other_m: float = 0.5
    sand_base_volume_m3: float = 0.0
    sand_compaction_coeff: float = 1.3
    sand_truck_step_m3: float = 20.0
    sand_items: list[dict[str, Any]] | None = None
    geotextile_area_m2: float = 0.0
    geotextile_overlap_coeff: float = 1.10
    geotextile_roll_area_m2: float = 100.0
    communications_length_calc_method: str = "legacy_direct_length"
    communications_length_m: float = 0.0
    communications_pipe_items: list[dict[str, Any]] | None = None
    axis_marking_shifts: float = 0.0
    excavator_shifts: float = 0.0
    geotextile_laying_area_m2: float = 0.0
    geotextile_laying_overlap_coeff: float = 1.0
    manual_excavation_quantity_for_estimate_m3: float | None = None
    consumables_calc_method: str = "legacy_fixed_amount"
    consumables_rate: float = 0.0
    consumables_amount: float = 0.0
    enabled_lines: list[str] | None = None
    quantity_overrides: dict[str, float] = field(default_factory=dict)
    line_name_overrides: dict[str, str] = field(default_factory=dict)
    internal_prices: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EarthworksInput":
        return cls(**data)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")
        if self.excavator_shifts_calc_method not in {
            "legacy_manual_shifts",
            "standard_volume_productivity",
        }:
            raise ValueError(
                "excavator_shifts_calc_method must be legacy_manual_shifts or standard_volume_productivity"
            )
        if self.manual_excavation_calc_method not in {
            "legacy_manual_override",
            "standard_routes",
        }:
            raise ValueError(
                "manual_excavation_calc_method must be legacy_manual_override or standard_routes"
            )
        if self.communications_length_calc_method not in {
            "legacy_direct_length",
            "pipe_items",
        }:
            raise ValueError(
                "communications_length_calc_method must be legacy_direct_length or pipe_items"
            )
        if self.consumables_calc_method not in {
            "legacy_fixed_amount",
            "section_total_rate",
        }:
            raise ValueError(
                "consumables_calc_method must be legacy_fixed_amount or section_total_rate"
            )

        _require_non_negative("pit_area_m2", self.pit_area_m2)
        _require_positive(
            "excavator_productivity_m3_per_shift",
            self.excavator_productivity_m3_per_shift,
        )
        _require_positive("manual_refinement_depth_m", self.manual_refinement_depth_m)
        for name in (
            "manual_trench_depth_k1_m",
            "manual_trench_depth_k2_m",
            "manual_trench_depth_water_m",
            "manual_trench_depth_eo_m",
            "manual_trench_depth_other_m",
        ):
            _require_non_negative(name, getattr(self, name))
        _require_non_negative("sand_base_volume_m3", self.sand_base_volume_m3)
        _require_positive("sand_compaction_coeff", self.sand_compaction_coeff)
        _require_positive("sand_truck_step_m3", self.sand_truck_step_m3)
        _require_non_negative("geotextile_area_m2", self.geotextile_area_m2)
        _require_positive("geotextile_overlap_coeff", self.geotextile_overlap_coeff)
        _require_positive("geotextile_roll_area_m2", self.geotextile_roll_area_m2)
        _require_positive("geotextile_laying_overlap_coeff", self.geotextile_laying_overlap_coeff)
        _require_non_negative("communications_length_m", self.communications_length_m)
        if self.communications_length_calc_method == "pipe_items":
            if not self.communications_pipe_items:
                raise ValueError("communications_pipe_items is required for pipe_items")
            for index, item in enumerate(self.communications_pipe_items):
                prefix = f"communications_pipe_items[{index}]"
                if not item.get("code"):
                    raise ValueError(f"{prefix}.code is required")
                if item.get("total_length_m") is not None:
                    _require_non_negative(f"{prefix}.total_length_m", item["total_length_m"])
                else:
                    _require_non_negative(f"{prefix}.pipe_length_m", item.get("pipe_length_m"))
                    _require_non_negative(f"{prefix}.quantity", item.get("quantity"))
        _require_non_negative("axis_marking_shifts", self.axis_marking_shifts)
        _require_non_negative("excavator_shifts", self.excavator_shifts)
        if self.excavator_shifts_calc_method == "standard_volume_productivity" and not self.pit_items:
            # Only required for the area*depth fallback (calculate_excavator_shifts_context's
            # `else` branch) - when pit_items gives ready per-pit volumes directly, depth never
            # enters that formula. Still echoed into the result as a control value when given
            # (see calculate_earthworks's "volumes" block), just no longer required to be present.
            _require_non_negative("pit_excavation_depth_m", self.pit_excavation_depth_m)
        _require_non_negative(
            "geotextile_laying_area_m2",
            self.geotextile_laying_area_m2,
        )
        _require_non_negative("consumables_amount", self.consumables_amount)
        _require_non_negative("consumables_rate", self.consumables_rate)

        if self.manual_excavation_quantity_for_estimate_m3 is not None:
            _require_non_negative(
                "manual_excavation_quantity_for_estimate_m3",
                self.manual_excavation_quantity_for_estimate_m3,
            )

        for key, value in self.internal_prices.items():
            _require_non_negative(f"internal_prices.{key}", value)

        for key, value in self.quantity_overrides.items():
            _require_non_negative(f"quantity_overrides.{key}", value)

        for index, item in enumerate(self.pit_items or []):
            prefix = f"pit_items[{index}]"
            if not item.get("context"):
                raise ValueError(f"{prefix}.context is required")
            _require_non_negative(f"{prefix}.volume_m3", item.get("volume_m3"))

        for index, item in enumerate(self.sand_items or []):
            prefix = f"sand_items[{index}]"
            if not item.get("context"):
                raise ValueError(f"{prefix}.context is required")
            _require_non_negative(f"{prefix}.volume_m3", item.get("volume_m3"))

        if self.manual_excavation_calc_method == "standard_routes":
            _require_positive("trench_width_m", self.trench_width_m)
            if self.trench_volume_m3 is not None:
                _require_non_negative("trench_volume_m3", self.trench_volume_m3)
                return
            if not self.trench_routes:
                raise ValueError(
                    "trench_volume_m3 or trench_routes is required for standard_routes"
                )
            for index, route in enumerate(self.trench_routes):
                prefix = f"trench_routes[{index}]"
                if not route.get("route_code"):
                    raise ValueError(f"{prefix}.route_code is required")
                _require_non_negative(f"{prefix}.length_m", route.get("length_m"))
                _require_non_negative(f"{prefix}.depth_m", route.get("depth_m"))
                if route.get("volume_m3") is not None:
                    _require_non_negative(f"{prefix}.volume_m3", route.get("volume_m3"))
            return

        if self.trench_volume_m3 is not None:
            _require_non_negative("trench_volume_m3", self.trench_volume_m3)
            return

        _require_non_negative("trench_length_m", self.trench_length_m)
        _require_non_negative("trench_depth_m", self.trench_depth_m)
        _require_non_negative("trench_width_m", self.trench_width_m)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EstimateLineResult:
    code: str
    name: str
    unit: str
    quantity: float
    material_unit_price: float
    material_total: int
    work_unit_price: float
    work_total: int
    line_total: int
    price_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.price_code is None:
            result.pop("price_code")
        return result


def _round_money(value: Decimal | float | int) -> int:
    decimal_value = value if isinstance(value, Decimal) else _to_decimal(value)
    return int(decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _price(data: EarthworksInput, key: str) -> float:
    if key not in data.internal_prices:
        raise ValueError(f"internal_prices.{key} is required")
    return data.internal_prices[key]


def _quantity(data: EarthworksInput, key: str, default: float) -> float:
    return data.quantity_overrides.get(key, default)


def _line_name(data: EarthworksInput, code: str, default: str) -> str:
    return data.line_name_overrides.get(code, default)


def _line_enabled(data: EarthworksInput, code: str) -> bool:
    return data.enabled_lines is None or code in set(data.enabled_lines)


def calculate_manual_pit_volume(
    pit_area_m2: float,
    manual_refinement_depth_m: float = 0.08,
) -> float:
    result = _to_decimal(pit_area_m2) * _to_decimal(manual_refinement_depth_m)
    return _round_decimal(result)


def calculate_excavator_shifts(
    excavator_shifts_calc_method: str,
    excavator_shifts: float,
    pit_area_m2: float,
    pit_excavation_depth_m: float | None,
    excavator_productivity_m3_per_shift: float,
    pit_items: list[dict[str, Any]] | None = None,
) -> tuple[str, float | None, float]:
    if excavator_shifts_calc_method == "legacy_manual_shifts":
        return "legacy_manual_shifts", None, _round_decimal(_to_decimal(excavator_shifts))

    productivity = _to_decimal(excavator_productivity_m3_per_shift)

    if pit_items:
        # Given ready excavation volumes per item (real project case, 2026-07-26): a project can
        # give the pit's own excavated volume directly (e.g. main pit + footing pits), instead of
        # recomputing it from pit_area_m2 * pit_excavation_depth_m — stated project volumes always
        # win over recomputed geometry (same principle as trench_routes' volume_m3 override).
        machine_excavation_volume_m3 = _round_decimal(
            sum(_to_decimal(item["volume_m3"]) for item in pit_items)
        )
    else:
        pit_area = _to_decimal(pit_area_m2)
        pit_depth = _to_decimal(pit_excavation_depth_m)
        if pit_depth is None:
            raise ValueError("pit_excavation_depth_m is required for standard_volume_productivity")
        machine_excavation_volume_m3 = _round_decimal(pit_area * pit_depth)

    if machine_excavation_volume_m3 == 0:
        return "standard_volume_productivity", machine_excavation_volume_m3, 0.0

    calculated_shifts = ceil(machine_excavation_volume_m3 / float(productivity))
    return "standard_volume_productivity", machine_excavation_volume_m3, float(calculated_shifts)


def calculate_trench_volume(
    trench_volume_m3: float | None = None,
    trench_length_m: float | None = None,
    trench_depth_m: float | None = None,
    trench_width_m: float | None = None,
) -> float:
    if trench_volume_m3 is not None:
        return _round_decimal(_to_decimal(trench_volume_m3))

    length = _to_decimal(trench_length_m)
    depth = _to_decimal(trench_depth_m)
    width = _to_decimal(trench_width_m)

    if length is None or depth is None or width is None:
        raise ValueError(
            "Provide trench_volume_m3 or trench_length_m, trench_depth_m, trench_width_m"
        )

    return _round_decimal(length * depth * width)


def calculate_trench_routes(
    trench_routes: list[dict[str, Any]],
    trench_width_m: float,
) -> tuple[list[dict[str, Any]], float, list[str]]:
    route_results = []
    warnings: list[str] = []
    total = Decimal("0")
    width = _to_decimal(trench_width_m)

    for route in trench_routes:
        length = _to_decimal(route["length_m"])
        depth = _to_decimal(route["depth_m"])
        calculated_volume = length * depth * width
        # Optional direct volume_m3 per route (real project case, 2026-07-26): a PDF table
        # can print a ready м3 column that disagrees with length*depth*width for that same
        # row — real project data always wins over recomputed geometry (rule already
        # established elsewhere in this pipeline: don't substitute arithmetic for stated
        # values). When given, it takes priority; a mismatch is only logged as a warning,
        # never blocked — the estimator reviews every trench/communications row by hand
        # regardless (see feedback_communications_precision_not_needed memory).
        given_volume = route.get("volume_m3")
        if given_volume is not None:
            volume = _to_decimal(given_volume)
            delta = abs(volume - calculated_volume)
            if delta > Decimal("0.01"):
                warnings.append(
                    f"trench_routes.{route['route_code']}: given volume_m3 ({_round_decimal(volume)}) "
                    f"differs from length*depth*width ({_round_decimal(calculated_volume)}); "
                    "using the given value."
                )
        else:
            volume = calculated_volume
        total += volume
        route_results.append(
            {
                "route_code": route["route_code"],
                "name": route.get("name", route["route_code"]),
                "length_m": _round_decimal(length),
                "depth_m": _round_decimal(depth),
                "width_m": _round_decimal(width),
                "volume_m3": _round_decimal(volume),
                "calculated_volume_m3": _round_decimal(calculated_volume),
                # Context-only (real project case, 2026-07-26): a route's printed depth can be
                # measured from a different reference point (e.g. "от дна котлована" instead of
                # from ground/zero elevation) than the depth actually used above. Carried through
                # purely for the service memo — never used in any calculation here, since mixing
                # reference points into one arithmetic check would produce false mismatches.
                "depth_reference": route.get("depth_reference"),
            }
        )

    return route_results, _round_decimal(total), warnings


# Route name/route_code -> network type, for picking the right manual hand-dig depth
# coefficient below. Matches both Cyrillic and Latin K (real route_codes use Latin, e.g.
# "K2_K3_P10", while printed PDF/smeta names use Cyrillic, e.g. "К2, К3"). Order matters:
# checked top to bottom, first match wins.
_TRENCH_NETWORK_TYPE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("water", re.compile(r"(?:[ВV]1|\bВК\b|водопровод)", re.IGNORECASE)),
    # \bЭО\b alone misses real labels like "ЭО1"/"ЭО4" - Cyrillic letters and digits are both
    # \w, so there is no \b between "О" and "1" for \bЭО\b to match on. \bЭО\d* (leading
    # boundary only, digits optional after) covers "ЭО", "ЭО1", "ЭО1; ЭО2; ЭО3", etc.
    ("eo", re.compile(r"(?:\bЭО\d*|электр|эл\.?\s*кабел)", re.IGNORECASE)),
    ("k1", re.compile(r"[КK]1(?!\d)", re.IGNORECASE)),
    ("k2", re.compile(r"[КK]2(?!\d)", re.IGNORECASE)),
]


def detect_trench_network_type(route_code: str, name: str | None) -> str:
    """Best-effort network-type guess from a trench route's own label. Approximate by design -
    real project categorization (see manual_trench_depth coefficients' docstring) is often more
    granular than our extracted route-level data, so this is a reasonable bucket, not a precise
    match. Falls back to "other" (and its own, separately reviewable coefficient) for anything
    unrecognized, rather than guessing wrong."""
    text = f"{route_code} {name or ''}"
    for network_type, pattern in _TRENCH_NETWORK_TYPE_PATTERNS:
        if pattern.search(text):
            return network_type
    return "other"


def calculate_trench_manual_portion(
    trench_routes_result: list[dict[str, Any]],
    trench_width_m: float,
    manual_trench_depth_k1_m: float,
    manual_trench_depth_k2_m: float,
    manual_trench_depth_water_m: float,
    manual_trench_depth_eo_m: float,
    manual_trench_depth_other_m: float,
) -> tuple[float, list[dict[str, Any]]]:
    """Manual (hand-dig) portion of trench excavation: NOT the full trench volume (that's mostly
    machine-dug), just each route's length x its network type's hand-dig depth x width -
    matching the real formula confirmed in ТРЦ/ЮСВ/АРК (2026-08-09): manual excavation =
    pit refinement layer + SUM(route_length x manual_depth_by_network_type x 0.4m width).
    Real coefficients found (length x depth x width per network, not the excavator's full cut):
    ТРЦ К1=0.6 К2=1.0 В1=1.6 ЭО=0.7 | ЮСВ К1=0.2 К2=0.2 ВК=1.6 ЭО=0.6 | АРК one flat 0.5 for
    everything (no per-network breakdown in that project). Defaults here are the ТРЦ/ЮСВ average
    per matching network (АРК's flat value reused as the "other/unrecognized" fallback)."""
    depth_by_type = {
        "k1": manual_trench_depth_k1_m,
        "k2": manual_trench_depth_k2_m,
        "water": manual_trench_depth_water_m,
        "eo": manual_trench_depth_eo_m,
        "other": manual_trench_depth_other_m,
    }
    width = _to_decimal(trench_width_m)
    total = Decimal("0")
    breakdown: list[dict[str, Any]] = []
    for route in trench_routes_result:
        network_type = detect_trench_network_type(route["route_code"], route.get("name"))
        depth_coeff = _to_decimal(depth_by_type[network_type])
        portion = _to_decimal(route["length_m"]) * depth_coeff * width
        total += portion
        breakdown.append(
            {
                "route_code": route["route_code"],
                "network_type": network_type,
                "manual_depth_coeff_m": float(depth_coeff),
                "manual_portion_m3": _round_decimal(portion),
            }
        )
    return _round_decimal(total), breakdown


def calculate_manual_excavation_total(
    manual_pit_volume_m3: float,
    trench_manual_portion_m3: float,
) -> float:
    result = _to_decimal(manual_pit_volume_m3) + _to_decimal(trench_manual_portion_m3)
    return _round_decimal(result)


def calculate_communications_length(
    communications_length_calc_method: str,
    communications_length_m: float,
    communications_pipe_items: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], float]:
    if communications_length_calc_method == "legacy_direct_length":
        return [], _round_decimal(_to_decimal(communications_length_m))

    if not communications_pipe_items:
        raise ValueError("communications_pipe_items is required for pipe_items")

    item_results = []
    total = Decimal("0")
    for item in communications_pipe_items:
        include = item.get("include_in_communications", True)
        if item.get("total_length_m") is not None:
            item_total = _to_decimal(item["total_length_m"])
            pipe_length = item.get("pipe_length_m")
            quantity = item.get("quantity")
        else:
            pipe_length_decimal = _to_decimal(item["pipe_length_m"])
            quantity_decimal = _to_decimal(item["quantity"])
            item_total = pipe_length_decimal * quantity_decimal
            pipe_length = _round_decimal(pipe_length_decimal)
            quantity = _round_decimal(quantity_decimal)

        if include:
            total += item_total

        item_results.append(
            {
                "code": item["code"],
                "name": item.get("name", item["code"]),
                "pipe_length_m": pipe_length,
                "quantity": quantity,
                "total_length_m": _round_decimal(item_total),
                "include_in_communications": include,
            }
        )

    return item_results, _round_decimal(total)


def calculate_compacted_sand(volume_m3: float, compaction_coeff: float = 1.3) -> float:
    result = _to_decimal(volume_m3) * _to_decimal(compaction_coeff)
    return _round_decimal(result)


def round_up_to_step(value: float, step: float) -> int:
    _require_non_negative("value", value)
    _require_positive("step", step)
    return int(ceil(value / step) * step)


def calculate_geotextile_with_overlap(
    geotextile_area_m2: float,
    overlap_coeff: float = 1.10,
) -> float:
    result = _to_decimal(geotextile_area_m2) * _to_decimal(overlap_coeff)
    return _round_decimal(result)


def calculate_rolls(area_m2: float, roll_area_m2: float) -> int:
    _require_non_negative("area_m2", area_m2)
    _require_positive("roll_area_m2", roll_area_m2)
    return int(ceil(area_m2 / roll_area_m2))


def calculate_line(
    code: str,
    name: str,
    unit: str,
    quantity: float,
    material_unit_price: float = 0.0,
    work_unit_price: float = 0.0,
    price_code: str | None = None,
) -> EstimateLineResult:
    quantity_rounded = _round_decimal(_to_decimal(quantity))
    material_total = _round_money(
        _to_decimal(quantity_rounded) * _to_decimal(material_unit_price)
    )
    work_total = _round_money(_to_decimal(quantity_rounded) * _to_decimal(work_unit_price))

    return EstimateLineResult(
        code=code,
        name=name,
        unit=unit,
        quantity=quantity_rounded,
        material_unit_price=material_unit_price,
        material_total=material_total,
        work_unit_price=work_unit_price,
        work_total=work_total,
        line_total=material_total + work_total,
        price_code=price_code,
    )


def calculate_internal_estimate_lines(
    data: EarthworksInput,
    volume_result: dict[str, Any],
) -> list[EstimateLineResult]:
    manual_excavation_quantity = (
        data.manual_excavation_quantity_for_estimate_m3
        if data.manual_excavation_calc_method == "legacy_manual_override"
        and data.manual_excavation_quantity_for_estimate_m3 is not None
        else volume_result["manual_excavation_total_m3"]
    )
    sand_order_volume_m3 = _quantity(
        data,
        "sand_order_volume_m3",
        volume_result["sand_order_volume_m3"],
    )
    geotextile_material_quantity_m2 = _quantity(
        data,
        "geotextile_material_quantity_m2",
        volume_result["geotextile_rolls"] * data.geotextile_roll_area_m2,
    )
    communications_length_m = volume_result["communications_length_m"]
    excavator_shifts = volume_result["excavator_shifts"]

    lines = []

    if _line_enabled(data, "axis_marking"):
        lines.append(
            calculate_line(
                code="axis_marking",
                name=_line_name(
                    data,
                    "axis_marking",
                    "Вынос осей фундамента, котлована на участок",
                ),
                unit="смена",
                quantity=data.axis_marking_shifts,
                work_unit_price=_price(data, "axis_marking_work_unit_price"),
                price_code="axis_marking_shift",
            )
        )
    if _line_enabled(data, "excavator_jcb"):
        lines.append(
            calculate_line(
                code="excavator_jcb",
                name=_line_name(
                    data,
                    "excavator_jcb",
                    "Механизированная разработка грунта, Экскаватор JCB",
                ),
                unit="смена",
                quantity=excavator_shifts,
                material_unit_price=_price(data, "excavator_material_unit_price"),
                work_unit_price=_price(data, "excavator_work_unit_price"),
                price_code="excavator_jcb_shift",
            )
        )
    if _line_enabled(data, "manual_excavation"):
        lines.append(
            calculate_line(
                code="manual_excavation",
                name=_line_name(data, "manual_excavation", "Разработка грунта вручную"),
                unit="м3",
                quantity=manual_excavation_quantity,
                work_unit_price=_price(data, "manual_excavation_work_unit_price"),
                price_code="manual_excavation_m3",
            )
        )
    if _line_enabled(data, "geotextile_laying"):
        geotextile_laying_quantity = _round_decimal(
            _to_decimal(data.geotextile_laying_area_m2) * _to_decimal(data.geotextile_laying_overlap_coeff)
        )
        lines.append(
            calculate_line(
                code="geotextile_laying",
                name=_line_name(data, "geotextile_laying", "Укладка геотекстиля"),
                unit="м2",
                quantity=geotextile_laying_quantity,
                work_unit_price=_price(data, "geotextile_laying_work_unit_price"),
                price_code="geotextile_laying_m2",
            )
        )
    if _line_enabled(data, "geotextile_material"):
        legacy_material_work_price = (
            _price(data, "geotextile_material_work_unit_price")
            if not _line_enabled(data, "geotextile_laying")
            and "geotextile_material_work_unit_price" in data.internal_prices
            else 0.0
        )
        lines.append(
            calculate_line(
                code="geotextile_material",
                name=_line_name(
                    data,
                    "geotextile_material",
                    "Геотекстиль Дорнит 300 г.м2 (100м2)",
                ),
                unit="м2",
                quantity=geotextile_material_quantity_m2,
                material_unit_price=_price(data, "geotextile_material_unit_price"),
                work_unit_price=legacy_material_work_price,
                price_code="geotextile_dornit_300_m2",
            )
        )
    if _line_enabled(data, "sand_filling"):
        lines.append(
            calculate_line(
                code="sand_filling",
                name=_line_name(
                    data,
                    "sand_filling",
                    "Отсыпка дна котлована, засыпка под плитой песком с трамбованием",
                ),
                unit="м3",
                quantity=sand_order_volume_m3,
                work_unit_price=_price(data, "sand_filling_work_unit_price"),
                price_code="sand_filling_work_m3",
            )
        )
    if _line_enabled(data, "sand_material"):
        lines.append(
            calculate_line(
                code="sand_material",
                name=_line_name(data, "sand_material", "Песок строительный"),
                unit="м3",
                quantity=sand_order_volume_m3,
                material_unit_price=_price(data, "sand_material_unit_price"),
                price_code="sand_m3",
            )
        )
    if _line_enabled(data, "sand_manual_moving"):
        lines.append(
            calculate_line(
                code="sand_manual_moving",
                name=_line_name(data, "sand_manual_moving", "Перемещение песка вручную"),
                unit="м3",
                quantity=sand_order_volume_m3,
                work_unit_price=_price(data, "sand_manual_moving_work_unit_price"),
                price_code="sand_manual_moving_m3",
            )
        )
    if _line_enabled(data, "communications_work"):
        lines.append(
            calculate_line(
                code="communications_work",
                name=_line_name(
                    data,
                    "communications_work",
                    "Закладка технологических входов коммуникаций до границы дома",
                ),
                unit="мп",
                quantity=communications_length_m,
                work_unit_price=_price(data, "communications_work_unit_price"),
                price_code="communications_installation_m",
            )
        )
    if _line_enabled(data, "communications_material"):
        lines.append(
            calculate_line(
                code="communications_material",
                name=_line_name(
                    data,
                    "communications_material",
                    "Материалы для устройства входов коммуникаций",
                ),
                unit="мп",
                quantity=communications_length_m,
                material_unit_price=_price(data, "communications_material_unit_price"),
                price_code="communications_material_m",
            )
        )
    if _line_enabled(data, "consumables"):
        consumables_amount = data.consumables_amount
        if data.consumables_calc_method == "section_total_rate":
            direct_cost_base = sum(line.line_total for line in lines)
            consumables_amount = _round_money(
                _to_decimal(direct_cost_base) * _to_decimal(data.consumables_rate)
            )
        lines.append(
            calculate_line(
                code="consumables",
                name=_line_name(
                    data,
                    "consumables",
                    "Расходные материалы, амортизация инструмента",
                ),
                unit="комплект",
                quantity=1,
                material_unit_price=consumables_amount,
            )
        )

    return lines


def calculate_internal_totals(lines: list[EstimateLineResult]) -> dict[str, int]:
    internal_materials_total = sum(line.material_total for line in lines)
    internal_works_total = sum(line.work_total for line in lines)

    return {
        "internal_materials_total": internal_materials_total,
        "internal_works_total": internal_works_total,
        "internal_section_total": internal_materials_total + internal_works_total,
    }


def calculate_earthworks(data: EarthworksInput) -> dict[str, Any]:
    (
        excavator_shifts_source,
        machine_excavation_volume_m3,
        excavator_shifts,
    ) = calculate_excavator_shifts(
        data.excavator_shifts_calc_method,
        data.excavator_shifts,
        data.pit_area_m2,
        data.pit_excavation_depth_m,
        data.excavator_productivity_m3_per_shift,
        data.pit_items,
    )

    trench_routes_result: list[dict[str, Any]] = []
    trench_route_warnings: list[str] = []
    trench_volume_source = "legacy"
    if data.manual_excavation_calc_method == "standard_routes":
        if data.trench_volume_m3 is not None:
            trench_volume_m3 = calculate_trench_volume(trench_volume_m3=data.trench_volume_m3)
            trench_volume_source = "spec_volume"
        else:
            trench_routes_result, trench_volume_m3, trench_route_warnings = calculate_trench_routes(
                data.trench_routes or [],
                data.trench_width_m,
            )
            trench_volume_source = "routes_calculated"
    else:
        trench_volume_m3 = calculate_trench_volume(
            trench_volume_m3=data.trench_volume_m3,
            trench_length_m=data.trench_length_m,
            trench_depth_m=data.trench_depth_m,
            trench_width_m=data.trench_width_m,
        )
        trench_volume_source = (
            "legacy_direct_volume"
            if data.trench_volume_m3 is not None
            else "legacy_dimensions"
        )
    manual_pit_volume_m3 = calculate_manual_pit_volume(
        data.pit_area_m2,
        data.manual_refinement_depth_m,
    )
    trench_manual_depth_breakdown: list[dict[str, Any]] = []
    if trench_routes_result:
        # Real per-route data available (standard_routes + trench_routes, not a flat
        # trench_volume_m3 override) - use the real manual-portion formula instead of counting
        # the whole excavator-dug trench as hand labor.
        trench_manual_portion_m3, trench_manual_depth_breakdown = calculate_trench_manual_portion(
            trench_routes_result,
            data.trench_width_m,
            data.manual_trench_depth_k1_m,
            data.manual_trench_depth_k2_m,
            data.manual_trench_depth_water_m,
            data.manual_trench_depth_eo_m,
            data.manual_trench_depth_other_m,
        )
    else:
        # Legacy paths (flat trench_volume_m3/dimensions, no named routes): no way to tell
        # which network a trench belongs to, so there is nothing to categorize - keep the old
        # 100%-of-trench-volume behavior rather than guessing at an unknown breakdown.
        trench_manual_portion_m3 = trench_volume_m3
    manual_excavation_total_m3 = calculate_manual_excavation_total(
        manual_pit_volume_m3,
        trench_manual_portion_m3,
    )

    sand_items_raw_total_m3 = 0.0
    if data.sand_items:
        # Given ready sand quantities per item (real project case, 2026-07-26): a project can
        # give sand backfill volumes directly by category (e.g. wall pazukha + trench bottom
        # combined, plus a separate footing-pit category) that don't map 1:1 onto the base/trench
        # split below — sum them first into one raw total, then apply the single compaction
        # coefficient once, same "sum then compact" math as before, just from a different source.
        sand_source = "items"
        sand_items_raw_total_m3 = _round_decimal(
            sum(_to_decimal(item["volume_m3"]) for item in data.sand_items)
        )
        compacted_sand_base_m3 = 0.0
        compacted_sand_trenches_m3 = 0.0
        sand_total_m3 = calculate_compacted_sand(
            sand_items_raw_total_m3,
            data.sand_compaction_coeff,
        )
    else:
        sand_source = "legacy"
        compacted_sand_base_m3 = calculate_compacted_sand(
            data.sand_base_volume_m3,
            data.sand_compaction_coeff,
        )
        # Real ТРЦ formula (2026-08-09): trench sand backfill is compacted from the same
        # manual-portion figure as the manual-excavation line above (Q30=T27*1.3 in her sheet),
        # not the full machine-dug trench volume - only the hand-finished extra depth needs
        # backfilling this way.
        compacted_sand_trenches_m3 = calculate_compacted_sand(
            trench_manual_portion_m3,
            data.sand_compaction_coeff,
        )
        sand_total_m3 = _round_decimal(
            _to_decimal(compacted_sand_base_m3) + _to_decimal(compacted_sand_trenches_m3)
        )
    sand_order_volume_m3 = round_up_to_step(sand_total_m3, data.sand_truck_step_m3)

    geotextile_with_overlap_m2 = calculate_geotextile_with_overlap(
        data.geotextile_area_m2,
        data.geotextile_overlap_coeff,
    )
    geotextile_rolls = calculate_rolls(
        geotextile_with_overlap_m2,
        data.geotextile_roll_area_m2,
    )
    communications_pipe_items_result, communications_length_m = calculate_communications_length(
        data.communications_length_calc_method,
        data.communications_length_m,
        data.communications_pipe_items,
    )

    volume_result = {
        "excavator_shifts_calc_method": data.excavator_shifts_calc_method,
        "excavator_shifts_source": excavator_shifts_source,
        "pit_excavation_depth_m": data.pit_excavation_depth_m,
        "machine_excavation_volume_m3": machine_excavation_volume_m3,
        "excavator_productivity_m3_per_shift": data.excavator_productivity_m3_per_shift,
        "excavator_shifts": excavator_shifts,
        "pit_items": data.pit_items or [],
        "manual_excavation_calc_method": data.manual_excavation_calc_method,
        "manual_pit_volume_m3": manual_pit_volume_m3,
        "manual_refinement_depth_m": data.manual_refinement_depth_m,
        "trench_width_m": data.trench_width_m,
        "trench_volume_source": trench_volume_source,
        "trench_routes": trench_routes_result,
        "trench_volume_total_m3": trench_volume_m3,
        "trench_volume_m3": trench_volume_m3,
        "trench_manual_portion_m3": trench_manual_portion_m3,
        "trench_manual_depth_breakdown": trench_manual_depth_breakdown,
        "manual_trench_depth_k1_m": data.manual_trench_depth_k1_m,
        "manual_trench_depth_k2_m": data.manual_trench_depth_k2_m,
        "manual_trench_depth_water_m": data.manual_trench_depth_water_m,
        "manual_trench_depth_eo_m": data.manual_trench_depth_eo_m,
        "manual_trench_depth_other_m": data.manual_trench_depth_other_m,
        "manual_excavation_total_m3": manual_excavation_total_m3,
        "sand_source": sand_source,
        "sand_items": data.sand_items or [],
        "sand_items_raw_total_m3": sand_items_raw_total_m3,
        "compacted_sand_base_m3": compacted_sand_base_m3,
        "compacted_sand_trenches_m3": compacted_sand_trenches_m3,
        "sand_total_m3": sand_total_m3,
        "sand_order_volume_m3": sand_order_volume_m3,
        "geotextile_with_overlap_m2": geotextile_with_overlap_m2,
        "geotextile_rolls": geotextile_rolls,
        "communications_length_calc_method": data.communications_length_calc_method,
        "communications_pipe_items": communications_pipe_items_result,
        "communications_length_m": communications_length_m,
        "trench_routes_warnings": trench_route_warnings,
    }
    estimate_lines = calculate_internal_estimate_lines(data, volume_result)
    internal_totals = calculate_internal_totals(estimate_lines)

    return {
        "inputs": data.to_dict(),
        "volume_result": volume_result,
        "estimate_lines": [line.to_dict() for line in estimate_lines],
        "internal_totals": internal_totals,
        "warnings": trench_route_warnings,
    }
