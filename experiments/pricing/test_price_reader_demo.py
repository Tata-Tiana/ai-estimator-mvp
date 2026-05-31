from __future__ import annotations

from pathlib import Path

from price_reader import (
    load_price_registry,
    load_project_price_overrides,
    resolve_price,
)


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "output" / "price_registry_filled_v3.xlsx"


def main() -> None:
    registry = load_price_registry(REGISTRY_PATH)
    overrides = load_project_price_overrides(REGISTRY_PATH)

    checks = [
        ("bitumen_primer_aquamast_18l_item", "2865"),
        ("concrete_b22_5_m3", "6400"),
        ("unknown_test_code", "123"),
        ("concrete_delivery_trip", "7500"),
    ]

    print(f"registry: {REGISTRY_PATH}")
    print(f"loaded price_registry codes: {len(registry)}")
    print(f"loaded project overrides: {len(overrides)}")
    print("")

    for price_code, fallback in checks:
        resolved = resolve_price(price_code, fallback, registry, overrides)
        print(f"{price_code}")
        print(f"  price: {resolved['price']}")
        print(f"  source: {resolved['source']}")
        print(f"  found: {resolved['found']}")
        if resolved["warning"]:
            print(f"  warning: {resolved['warning']}")
        print("")


if __name__ == "__main__":
    main()
