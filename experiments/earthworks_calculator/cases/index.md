# Кейсы земляных работ

## usv_yusupovo_village

- разобран с Еленой;
- эталонный кейс;
- `validated_with_elena`: `true`;
- `confidence`: `high`;
- включает коммуникации;
- включает отдельную укладку геотекстиля;
- ручная разработка для строки сметы использует legacy-режим и явное количество `44.695`.

## horoshevka_14

- не разбирался с Еленой;
- повторение сметы;
- `validated_with_elena`: `false`;
- `confidence`: `medium`;
- нет коммуникаций в серой итоговой части;
- работа геотекстиля внутри материала;
- используются overrides для ручной разработки, песка и геотекстиля.

## test_communications_pipe_items

- тест production-стандарта длины коммуникаций;
- длина коммуникаций считается из списка труб спецификации;
- проверяет, что `communications_work` и `communications_material` берут рассчитанную длину;
- прямой `communications_length_m` не используется как ручной ввод.

## test_excavator_shifts_standard

- тест production-стандарта расчёта смен экскаватора;
- объём механизированной выемки считается как `pit_area_m2 * pit_excavation_depth_m`;
- производительность экскаватора — системная настройка `80 м3/смена`;
- проверяет формулу `ceil((pit_area_m2 * pit_excavation_depth_m) / 80)`;
- прямой `excavator_shifts` не используется как ручной ввод.

## test_manual_excavation_standard_routes

- тест production-стандарта ручной разработки грунта;
- траншеи считаются по трассам `K1`, `K2`, `VK`, `EO`;
- `manual_excavation_quantity_for_estimate_m3` не используется;
- проверяет формулу `pit_area_m2 * 0.08 + sum(length_m * depth_m * 0.4)`.

## test_manual_excavation_spec_trench_volume

- тест production-стандарта ручной разработки грунта;
- объём траншей берётся готовым значением `trench_volume_m3` из спецификации;
- `trench_routes` не требуются, если готовый объём найден;
- проверяет, что ручная разработка и песок в траншеи используют один и тот же `trench_volume_total_m3`.
