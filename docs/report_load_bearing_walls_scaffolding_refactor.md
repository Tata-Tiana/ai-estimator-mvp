# Отчёт: production-расчёт подмостей/лесов в несущих стенах

Дата: 2026-06-09

## Что изменено

В калькуляторе `experiments/load_bearing_walls_lintels_calculator/` добавлен режим расчёта подмостей/лесов от количества этажей.

Старые прямые входы:

```text
scaffolding_setup_quantity
scaffolding_timber_quantity_m3
```

оставлены только для legacy-кейса сверки со старой сметой.

## Production-стандарт

Новый режим:

```text
scaffolding_calc_method = "floors_based"
```

Формулы:

```text
scaffolding_setup_quantity = floors_count * scaffolding_setup_units_per_floor
scaffolding_timber_quantity_m3 = floors_count * scaffolding_timber_m3_per_floor
```

Системные defaults:

```text
scaffolding_setup_units_per_floor = 1
scaffolding_timber_m3_per_floor = 1 м3
```

Классификация параметров:

| Параметр | Статус | Комментарий |
| --- | --- | --- |
| `floors_count` | AUTO_PROJECT | Количество этажей берётся из проекта/спецификации. |
| `scaffolding_setup_units_per_floor` | DEFAULT_VALUE | Методика Елены: 1 комплект на этаж. |
| `scaffolding_timber_m3_per_floor` | DEFAULT_VALUE | Методика Елены: 1 м3 пиломатериала на этаж. |
| `scaffolding_setup_quantity` | AUTO_CALCULATED | Рассчитывается от `floors_count`. |
| `scaffolding_timber_quantity_m3` | AUTO_CALCULATED | Рассчитывается от `floors_count`. |

## Legacy

Кейс `test_load_bearing_walls_lintels` использует:

```text
scaffolding_calc_method = "legacy_direct_quantity"
```

Это сохраняет старые итоговые суммы и старый `expected.json`.

## Новый тест

Создан кейс:

```text
experiments/load_bearing_walls_lintels_calculator/cases/test_scaffolding_floors_based/
```

Проверка:

```text
floors_count = 2
scaffolding_setup_quantity = 2
scaffolding_timber_quantity_m3 = 2
```

Строки сметы `scaffolding_setup_dismantling` и `scaffolding_timber_material` берут рассчитанные quantities из блока `calculation_blocks.scaffolding`.

## TODO

- Обновить `section_schema.py`.
- Добавить `floors_count` в `reviewed_parameters.xlsx`.
- Научить parser брать количество этажей из спецификации/проекта.
- Убрать `scaffolding_setup_quantity` и `scaffolding_timber_quantity_m3` из формы Елены как ручные production-поля.
- Показывать Елене `floors_count` и рассчитанные quantities как контроль.
