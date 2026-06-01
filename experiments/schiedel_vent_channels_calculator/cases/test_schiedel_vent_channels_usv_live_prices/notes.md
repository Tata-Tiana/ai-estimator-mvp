# Live prices case

Кейс проверяет режим `price_registry_with_fallback` для раздела Schiedel.

- Формулы калькулятора не меняются.
- Суммы могут отличаться от эталонного `test_schiedel_vent_channels_usv`.
- Цены ищутся по `price_code`: сначала `project_price_overrides`, затем `price_registry`, затем fallback из `input.json`.
- `expected.json` намеренно не добавлен: live-кейс является smoke-check для слоя цен, а не проверкой старых сумм.
