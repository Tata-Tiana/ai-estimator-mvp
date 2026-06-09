# Рефактор длины коммуникаций в земляных работах

Дата: 2026-06-09

## Что было

В старой логике раздела "Земляные работы" длина коммуникаций задавалась готовым числом:

```text
communications_length_m
```

Это значение напрямую использовалось в двух строках:

- `communications_work` — "Закладка технологических входов коммуникаций до границы дома";
- `communications_material` — "Материалы для устройства входов коммуникаций".

## Что стало production-стандартом

Добавлен режим:

```text
communications_length_calc_method = pipe_items
```

В этом режиме длина коммуникаций считается из спецификации труб:

```text
communications_length_m = sum(pipe_length_m * quantity)
```

Если позиция спецификации уже содержит готовую длину, используется:

```text
total_length_m
```

Позиции с `include_in_communications = false` не входят в итог.

## Формат входных данных

```json
{
  "code": "pipe_1m",
  "name": "Труба 1 м",
  "pipe_length_m": 1,
  "quantity": 12,
  "include_in_communications": true
}
```

или:

```json
{
  "code": "corrugated_pipe",
  "name": "Труба гофрированная",
  "total_length_m": 25,
  "include_in_communications": true
}
```

## Что считается автоматически

`communications_length_m` теперь является `AUTO_CALCULATED` в production-потоке.

Итоговая длина используется в строках:

- `communications_work.quantity`;
- `communications_material.quantity`.

## Legacy

Прямой ввод `communications_length_m` оставлен только для legacy-кейсов:

```text
communications_length_calc_method = legacy_direct_length
```

Кейс `usv_yusupovo_village` продолжает использовать прямое значение `115 м`, чтобы повторить старую смету. Старый `expected.json` не менялся.

## Новый тест

Создан кейс:

```text
experiments/earthworks_calculator/cases/test_communications_pipe_items/
```

Проверочный расчёт:

- труба 1 м: `1 * 12 = 12`;
- труба 2 м: `2 * 5 = 10`;
- труба 3 м: `3 * 4 = 12`;
- труба гофрированная: `25`;
- итоговая длина: `59 м`.

## TODO

- Обновить `section_schema.py`.
- Добавить `communications_pipe_items` в `reviewed_parameters.xlsx`.
- Научить parser искать трубы в спецификации КР-1.
- Убрать прямой `communications_length_m` из формы Елены как ручной ввод для production-потока.
- Показывать Елене таблицу труб и итоговую длину как контроль.
