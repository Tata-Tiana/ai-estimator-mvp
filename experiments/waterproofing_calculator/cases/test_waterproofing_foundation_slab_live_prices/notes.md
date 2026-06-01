# Гидроизоляция фундаментной плиты: live prices

Этот кейс проверяет режим `price_registry_with_fallback`.

Формулы совпадают со старым эталонным кейсом `test_waterproofing_foundation_slab`, но цены для строк с `price_code` резолвятся через:

```text
project_price_overrides
↓
price_registry
↓
input.json fallback
```

`expected.json` намеренно не используется: суммы live-режима могут отличаться от эталонной сметы из-за цен из `price_registry`.

В `result.json` и `result.md` нужно смотреть:

- `pricing_summary`;
- `unit_price_source`;
- `unit_price_original`;
- `unit_price_used`;
- `price_warning`.
