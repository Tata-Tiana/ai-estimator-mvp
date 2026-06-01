# Live prices case

Кейс проверяет режим `price_registry_with_fallback` для фундаментной плиты.

- Формулы калькулятора не меняются.
- Старый `expected.json` не используется, потому что live-цены могут отличаться.
- Цена ищется по `price_code`: `project_price_overrides`, затем `price_registry`, затем fallback из `input.json`.
