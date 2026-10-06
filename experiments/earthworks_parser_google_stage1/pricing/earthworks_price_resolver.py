from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pricing.earthworks_price_contract import ABSENT_STRUCTURAL_COMPONENTS, EARTHWORKS_PRICE_COMPONENTS
from source_paths import FALLBACK_LIVE_INPUT_PATH


SOURCE_LABELS_RU = {
    "price_registry": "price_registry",
    "base_case_fallback": "fallback: базовая цена из базового кейса",
    "manual_override": "manual: исправлено в текущей смете",
    "missing_price": "цена не найдена",
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fallback_prices() -> dict[str, float]:
    data = load_json(FALLBACK_LIVE_INPUT_PATH, {})
    raw_prices = data.get("internal_prices") or {}
    prices = {key: float(val) for key, val in raw_prices.items()}
    if "consumables_amount" in data:
        prices["consumables_amount"] = float(data["consumables_amount"])
    return prices


def registry_by_code(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for row in rows:
        code = row.get("price_code")
        if code and code not in result:
            result[code] = row
    return result


def resolve_earthworks_prices(
    job_dir: Path,
    registry_rows: list[dict[str, Any]],
    manual_overrides: dict[str, float] | None = None,
) -> dict[str, Any]:
    manual_overrides = manual_overrides or {}
    fallback = fallback_prices()
    registry = registry_by_code(registry_rows)
    resolved = []
    internal_prices: dict[str, float] = {}

    for component in EARTHWORKS_PRICE_COMPONENTS:
        price_from_registry = None
        fallback_price = None
        price = None
        source = "missing_price"
        price_registry_code = ""
        needs_attention = False
        comment = component.comment_ru

        if component.component_code in manual_overrides:
            price = manual_overrides[component.component_code]
            source = "manual_override"
        else:
            for code in component.price_registry_codes:
                row = registry.get(code)
                if not row:
                    continue
                if row.get("Ед. изм.") != component.unit:
                    continue
                if row.get("Цена") is None:
                    continue
                price_from_registry = float(row["Цена"])
                price = price_from_registry
                source = "price_registry"
                price_registry_code = code
                break
            if component.fallback_allowed and component.internal_price_key in fallback:
                fallback_price = fallback[component.internal_price_key]
            if price is None and fallback_price is not None:
                price = fallback_price
                source = "base_case_fallback"
            if price is None:
                needs_attention = component.required_for_calculation
                comment = "Цена не найдена. Заполните вручную на листе 02_Цены себестоимости."

        if price is not None and component.internal_price_key != "consumables_amount":
            internal_prices[component.internal_price_key] = price

        resolved.append(
            {
                **component.to_dict(),
                "price": price,
                "price_from_registry": price_from_registry,
                "fallback_price": fallback_price,
                "price_for_calculation": price,
                "source": source,
                "source_label_ru": SOURCE_LABELS_RU[source],
                "price_registry_code": price_registry_code,
                "manual_override": manual_overrides.get(component.component_code),
                "needs_attention": needs_attention,
                "comment_ru": comment,
            }
        )

    pricing_dir = job_dir / "pricing"
    pricing_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "resolved_components": resolved,
        "absent_structural_components": ABSENT_STRUCTURAL_COMPONENTS,
    }
    (pricing_dir / "earthworks_price_resolution.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (pricing_dir / "earthworks_internal_prices.json").write_text(
        json.dumps(internal_prices, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"resolution": payload, "internal_prices": internal_prices}
