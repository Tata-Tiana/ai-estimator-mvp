# Load Bearing Walls And Lintels Calculator Experiment

Экспериментальный детерминированный калькулятор раздела "Внешние и внутренние несущие стены, перемычки".

AI здесь не используется. Калькулятор считает только серую внутреннюю себестоимость: материалы, работы и итог раздела. Клиентская часть, рентабельность, НР/СП/ТН и коммерческие коэффициенты не считаются.

## Запуск

```bash
.venv/bin/python3 experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels
```

Проверка компиляции:

```bash
.venv/bin/python3 -m py_compile experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py
```

## Структура

```text
load_bearing_walls_lintels_calculator.py
run_load_bearing_walls_lintels_calc.py
cases/
  test_load_bearing_walls_lintels/
    input.json
    expected.json
    notes.md
  test_scaffolding_floors_based/
    input.json
    expected.json
    notes.md
  test_cutoff_waterproofing_spec_area/
    input.json
    expected.json
    notes.md
  test_lintel_spec_total_length/
    input.json
    expected.json
    notes.md
  test_lintel_concrete_spec_volume/
    input.json
    expected.json
    notes.md
  test_lintel_concrete_spec_volume_min_order/
    input.json
    expected.json
    notes.md
  test_floor_1_without_floor_2/
    input.json
    expected.json
    notes.md
  test_floor_2_load_bearing_walls_spec_volume/
    input.json
    expected.json
    notes.md
  test_flat_roof_parapet_vent_channels/
    input.json
    expected.json
    notes.md
  test_vent_chimney_spec_volume_thickness/
    input.json
    expected.json
    notes.md
  test_rebar_spec_length_by_floor_component/
    input.json
    expected.json
    notes.md
  test_main_walls_crane_from_delivery_trucks/
    input.json
    expected.json
    notes.md
  test_main_walls_crane_from_delivery_trucks_four/
    input.json
    expected.json
    notes.md
output/
  test_load_bearing_walls_lintels/
    load_bearing_walls_lintels_result.json
    load_bearing_walls_lintels_result.md
```

## Важные правила

- Старый кейс `test_load_bearing_walls_lintels` использует legacy-режим подмостей `legacy_direct_quantity`, где количества заданы напрямую для сверки с исходной сметой.
- Новый production-стандарт подмостей `floors_based`: `scaffolding_setup_quantity = floors_count * 1`, `scaffolding_timber_quantity_m3 = floors_count * 1 м3`.
- `floors_count` - проектный параметр, а `scaffolding_setup_units_per_floor = 1` и `scaffolding_timber_m3_per_floor = 1` - системные defaults.
- Старый расчёт отсечной гидроизоляции по длинам стен 400/250 мм сохранён как `legacy_lengths_by_wall_thickness`.
- Новый production-стандарт отсечной гидроизоляции `spec_area`: площадь под несущие стены берётся из спецификации как `cutoff_waterproofing_load_bearing_walls_area_m2`.
- Площадь отсечной гидроизоляции перегородок не включается в этот раздел и должна жить в отдельном разделе перегородок.
- Старый расчёт общей длины перемычек по списку `lintel_lengths_m` сохранён как `legacy_length_count_items`.
- Новый production-стандарт перемычек `spec_total_length`: `lintel_total_length_m` берётся готовым значением из спецификации.
- Резка U-блока остаётся в штуках: `u_block_quantity = lintel_total_length_m / gas_block_length_m`.
- Сечение бетонной части U-блока для перемычек - системный default: `lintel_section_width_m = 0.125`, `lintel_section_height_m = 0.125`. В production эти поля не спрашиваются у Елены.
- Старый расчёт бетона перемычек по длине и сечению сохранён как `legacy_length_section`.
- Новый production-стандарт бетона перемычек `spec_volume`: `lintel_concrete_spec_volume_m3` берётся из спецификации проекта, а закупочный объём считается как `max(1, ceil(lintel_concrete_spec_volume_m3))`.
- `lintel_concrete_min_order_volume_m3 = 1` - системный default закупки, в production не спрашивается у Елены.
- Старая логика арматуры кладки через геометрию стен сохранена как `legacy_wall_geometry`.
- Старая логика арматуры перемычек через `weight_kg` сохранена как `legacy_weight_items`.
- Новый production-стандарт арматуры `spec_length_items`: арматура берётся из спецификации в м.п. и разделяется по этажам, конструкциям, классу стали и диаметру.
- Арматура перегородок не входит в этот калькулятор; `component = partitions` отклоняется validation.
- Старое количество смен крана несущих стен сохранено как `legacy_manual_shifts`.
- Новый production-стандарт крана `delivery_trucks_threshold`: если `gas_block_delivery_trucks <= 3`, то `main_walls_crane_shifts = 1`; если доставок 4 или больше, то `main_walls_crane_shifts = 2`.
- MVP поддерживает только 1 или 2 этажа. `floors_count = 3` запрещён: 3-этажные дома вне MVP scope.
- `second_light_masonry` - legacy-название старого ЮСВ-кейса. В production используется блок `floor_2_load_bearing_walls`.
- Для production `floors_count = 1` выключает блок 2-го этажа, `floors_count = 2` включает его, а объём берётся из `floor_2_masonry_volume_m3`.
- Парапет в production включается от `flat_roof_enabled` и `parapet_masonry_volume_m3`.
- Обкладка вентканалов в production включается от `flat_roof_enabled` и `vent_chimney_gas_block_spec_volume_m3`.
- Production-геометрия вентканалов `spec_volume_thickness`: площадь работ считается как `vent_chimney_gas_block_spec_volume_m3 / 0.15`.
- `vent_chimney_block_thickness_m = 0.15` - системный default для блока 150 мм.
- `vent_chimney_segment_lengths_m`, `vent_chimney_rows` и `block_height_m` используются только как `DEPRECATED / LEGACY_CHECK_ONLY` в режиме `legacy_segments_rows`.
- Расходные материалы пока manual/fixed amount, потому что формула не подтверждена.
- Вывоз мусора и часть доставок пока задаются входными параметрами.
- Итоги раздела считаются по Excel-логике: суммируются raw-значения строк, затем округляется итог.
- Дополнительно выводится сумма отображённых округлённых строк, чтобы видеть разницу между raw totals и видимыми строками.

## Ожидаемый результат

```text
internal_materials_total_raw = 1550654.431
internal_materials_total = 1550654
internal_works_total_raw = 1121449
internal_works_total = 1121449
internal_section_total_raw = 2672103.431
internal_section_total = 2672103
```
