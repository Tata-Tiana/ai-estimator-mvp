# Flat Roof Calculator

Экспериментальный детерминированный калькулятор раздела:

```text
КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля
```

## Как запустить

```bash
.venv/bin/python3 experiments/flat_roof_calculator/run_case.py experiments/flat_roof_calculator/cases/test_flat_roof_usv
```

Если локальный Python запускается без venv:

```bash
python3 experiments/flat_roof_calculator/run_case.py experiments/flat_roof_calculator/cases/test_flat_roof_usv
```

## Что создаётся

```text
experiments/flat_roof_calculator/cases/test_flat_roof_usv/result.json
experiments/flat_roof_calculator/cases/test_flat_roof_usv/result.md
```

## Что считается

- только серая внутренняя себестоимость;
- материалы/механизмы;
- работы;
- итог раздела по реализованным строкам;
- raw и display значения отдельно;
- закупочные количества с округлением вверх там, где требуется.

## Что не считается

- клиентская/белая часть;
- коммерческие коэффициенты;
- налоги;
- уклонные плиты по геометрии кровли.

## Ручные параметры

- в legacy-режиме готовые totals кровли требуют проверки человеком;
- объёмы ЭППС 50 мм и SLOPE плит берутся как `supplier_required_volume_m3`;
- расходные материалы временно берутся как предоставленный raw total;
- логистика и снабжение временно берётся как предоставленный raw total;
- технический надзор берётся как предоставленный fixed work total;
- заготовительно-складские расходы берутся как предоставленный fixed work total;
- `roof_work_coeff` является параметром проекта и может меняться.

## Production roof geometry

Для production используется режим:

```text
roof_geometry_calc_method = "detailed_project_geometry"
```

Из проекта/спецификации приходят составляющие:

- `roof_area_level_1_m2`;
- `roof_area_level_2_m2`;
- `parapet_length_level_1_m`;
- `parapet_length_level_2_m`;
- `vent_wall_abutment_level_1_m`;
- `vent_wall_abutment_level_2_m`.

Калькулятор сам считает:

```text
roof_area_total_m2 =
roof_area_level_1_m2 + roof_area_level_2_m2

parapet_and_abutment_total_length_m =
parapet_length_level_1_m
+ parapet_length_level_2_m
+ vent_wall_abutment_level_1_m
+ vent_wall_abutment_level_2_m
```

Статусы параметров:

- `roof_area_level_1_m2`, `roof_area_level_2_m2`, `parapet_length_level_1_m`, `parapet_length_level_2_m`, `vent_wall_abutment_level_1_m`, `vent_wall_abutment_level_2_m` — `AUTO_PROJECT`;
- `roof_area_total_m2`, `parapet_and_abutment_total_length_m`, `calculated_roof_area_total_m2`, `calculated_parapet_and_abutment_total_length_m` — `AUTO_CALCULATED`;
- `input_roof_area_total_m2`, `input_parapet_and_abutment_total_length_m` — `CONTROL_OR_FALLBACK`;
- `roof_area_total_m2` и `parapet_and_abutment_total_length_m` как обязательные production input — `DEPRECATED / LEGACY_ONLY`.

`project_spec_roof_area_m2 = 294` остается отдельным контрольным значением и не используется автоматически без проверки человека.

Примыкания к стенам, ВК, вентканалам или вентшахтам, если проект дает их в `м.п.`, входят в
`parapet_and_abutment_total_length_m` и считаются строкой `Монтаж примыкания кровли из ПВХ мембраны`.
Отдельная строка `Монтаж примыкания к вентшахтам` по `шт` является optional/legacy и выводится только
когда `vent_shaft_abutment_count > 0`.

## Разделительный слой: правило Елены от 2026-09-18

Пороги проверяются по общей горизонтальной площади кровли до запаса, после суммирования
всех `roof_zones[]`, не по каждой зоне отдельно:

- до 300 м2 включительно: `geotextile_prof_300_flat`, площадь x 1.1, округление вверх
  до рулонов по 100 м2;
- больше 300 и до 430 м2 включительно: `fiberglass_mat_technonikol_100gr`, один рулон
  400 м2 независимо от площади с запасом;
- больше 430 м2: стеклохолст, площадь x 1.1, округление вверх до рулонов по 400 м2.

Площадь стеклохолста из сырой спецификации больше не является базой закупки основного слоя.
Геотекстиль 150 для примыканий и слои под ЦСП остаются отдельными, без изменения формул.

После дополнительного уточнения Елены геотекстиль 150 для парапетов и стен добавляется
во всех проектах с положительной длиной примыканий, без требования строки в спецификации:
`ceil(parapet_and_abutment_total_length_m * 1.1 / 100) * 100` м2.
База совпадает с количеством работы `pvc_membrane_abutment_installation` в м.п.
Округление выполняется один раз после суммирования зон; отдельный слой под ЦСП не вычитается.
Если примыканий нет, закупочная строка геотекстиля 150 не формируется.
Если есть ЦСП, его площадь исключается из площади основного слоя, чтобы не посчитать
его повторно; выбор материала и пороги всё равно проверяются по общей площади кровли.
Если один рулон по исключению меньше фактической площади основного слоя, результат
содержит предупреждение для проверки покрытия монтажной организацией.

## price_registry

У материальных строк есть `price_code`. Сейчас цены берутся из `input.json`.
Позже `price_code` можно связать с Google Sheets `price_registry`, не меняя смысловые формулы.

## Почему SLOPE плиты не считаются автоматически

Уклонные плиты зависят от схемы водоразделов, воронок, уклонов и раскладки производителя.
Для текущего MVP объёмы от поставщика фиксируются как ручной вход, чтобы не имитировать точность, которой пока нет.
