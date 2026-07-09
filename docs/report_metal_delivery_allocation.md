# Распределение доставки арматуры и металла на уровне box_calculator

Дата: 2026-06-09

## Контекст

После созвона с Еленой уточнено правило доставки арматуры/металла: доставка считается не внутри каждого отдельного раздела, а по общему весу металла коробки дома.

Старые строки вида `rebar_metal_delivery_trucks` в разделах остаются legacy/manual для старых кейсов и сверки с уже зафиксированной сметой.

## Почему это не ручной параметр фундаментной плиты

`rebar_metal_delivery_trucks` раньше был input-параметром в `foundation_slab_calculator`, потому что раздел считался отдельно.

Новый статус:

```text
rebar_metal_delivery_trucks:
  old_status = manual/input in foundation_slab
  new_status = AUTO_CALCULATED_BY_BOX
  show_in_review_form = false
  can_override = yes, only at box_calculator / project logistics settings level
```

Комментарий:

```text
Не вводится в разделе фундаментной плиты.
Рассчитывается по общему весу металла коробки и распределяется по разделам.
```

## Новое правило

```text
total_box_metal_weight_kg = sum(section.metal_weight_kg)
total_metal_delivery_trucks = ceil(total_box_metal_weight_kg / 10000)
```

Грузоподъёмность машины сейчас зафиксирована как `10000 кг`.

## Какие разделы отдают вес металла

Порядок по умолчанию:

1. `foundation_slab`
2. `load_bearing_walls_lintels`
3. `floor_slab_1`
4. `floor_slab_2`

Для фундаментной плиты использовать:

- `foundation_slab_rebar_delivery_weight_kg`, если есть новый standard-расчёт арматуры;
- временно `foundation_slab_rebar_control_weight_kg`, если новый вес ещё не отдан.

TODO для следующих этапов:

- `load_bearing_walls_lintels` должен отдавать `section_metal_weight_kg`;
- `floor_slab_1` должен отдавать `section_metal_weight_kg`;
- `floor_slab_2` должен отдавать `section_metal_weight_kg`;
- другие разделы добавлять только если там есть значимый металл.

## Распределение машин по разделам

Алгоритм:

- идти по разделам в порядке выполнения работ;
- считать накопленный вес металла;
- первую машину назначить первому разделу, где есть металл;
- каждую следующую машину назначать тому разделу, на котором накопленный вес пересёк очередную границу 10 тонн;
- если один раздел сам пересёк несколько границ, ему назначается несколько машин.

Пример:

```text
foundation_slab = 8263
load_bearing_walls_lintels = 2500
floor_slab_1 = 6000
floor_slab_2 = 3000

total = 19763
total_trucks = 2
```

Allocation:

```text
foundation_slab -> 1
load_bearing_walls_lintels -> 1
floor_slab_1 -> 0
floor_slab_2 -> 0
```

Вторая машина назначается на раздел несущих стен, потому что на нём накопленный вес пересёк 10 тонн.

## Реализация

Создан:

```text
experiments/box_calculator/
```

Основные файлы:

```text
box_calculator.py
metal_delivery_allocator.py
run_box_calculator.py
section_registry.py
```

В result.json блок называется:

```text
recommended_metal_delivery_allocation
```

Он содержит:

- `capacity_kg`;
- `total_box_metal_weight_kg`;
- `total_trucks`;
- `unit_price`;
- `total_delivery_cost`;
- `section_order`;
- распределение по разделам;
- warnings.

## Защита от задвоения

В текущем MVP allocation не прибавляется к старым итогам разделов.

Причина:

- legacy section totals могут уже содержать строку доставки металла;
- если добавить allocation сверху, доставка задвоится.

Поэтому result содержит warning:

```text
legacy section totals may already include metal delivery;
do not add allocation on top until Excel exporter supports replacement.
```

Будущий Excel exporter должен:

- убрать/заменить legacy line доставки металла в разделе;
- вставить allocated delivery line в нужный раздел;
- только после этого включать delivery allocation в итог коробки.

## Тест

Создан кейс:

```text
experiments/box_calculator/cases/test_metal_delivery_allocation/
```

Проверка:

```bash
.venv/bin/python3 experiments/box_calculator/run_box_calculator.py experiments/box_calculator/cases/test_metal_delivery_allocation
```

Ожидаемо:

```text
total_box_metal_weight_kg = 19763
total_trucks = 2
total_delivery_cost = 44000
foundation_slab allocated_trucks = 1
load_bearing_walls_lintels allocated_trucks = 1
comparison = 12 ok / 0 mismatch
```
