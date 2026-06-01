# Notes: Schiedel Vent Channels Calculator

- Калькулятор считает только серую внутреннюю себестоимость.
- Клиентская часть не считается.
- Нулевые строки структуры обязательно добавляются.
- Суммы `1053`, `536`, `14746`, `18959` не использовать.
- Schiedel material counts are manual/specification inputs.
- Количества `24` и `8` не выводятся автоматически из контрольных правых чисел.
- No Excel cell references.
- Деньги считаются через Decimal и ROUND_HALF_UP.
- Raw и display значения хранятся отдельно.
- `locked_case_prices` — режим для проверки старой эталонной сметы.
- `price_registry_with_fallback` — live-режим для будущего MVP с актуальными ценами.
- Live-суммы могут отличаться от старого expected, потому что часть цен берётся из `price_registry`.
- Для кладки используется `price_code = schiedel_masonry_work_m`; если его нет в прайсе, live-режим должен уходить во fallback input.
