from experiments.full_estimate_review_pipeline import build_review_workbook_from_contracts
from experiments.full_estimate_review_pipeline.review_to_calculator.core.rebar_item_defaults import (
    REBAR_KG_PER_M_BY_DIAMETER,
    REBAR_ROD_LENGTH_BY_DIAMETER,
    fill_rebar_catalog_defaults,
)


def test_diameter_14_is_filled_from_shared_rebar_catalog() -> None:
    result = fill_rebar_catalog_defaults(
        {"diameter_mm": 14, "kg_per_meter": None, "rod_length_m": None},
        section="foundation_slab",
    )

    assert result["kg_per_meter"] == 1.21
    assert result["rod_length_m"] == 11.7


def test_review_workbook_and_calculators_use_same_rebar_catalog() -> None:
    assert build_review_workbook_from_contracts.GOST_REBAR_KG_PER_METER is REBAR_KG_PER_M_BY_DIAMETER
    assert build_review_workbook_from_contracts.GOST_REBAR_ROD_LENGTH_M is REBAR_ROD_LENGTH_BY_DIAMETER
