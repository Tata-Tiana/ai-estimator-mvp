# Flat Roof Calculator

Экспериментальный детерминированный калькулятор раздела:

```text
КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля
```

## Как запустить

```bash
../.venv/bin/python3 experiments/flat_roof_calculator/run_case.py experiments/flat_roof_calculator/cases/test_flat_roof_usv
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
- временная дверь как индивидуальная case-specific строка;
- уклонные плиты по геометрии кровли.

## Ручные параметры

- площадь кровли требует проверки человеком;
- объёмы ЭППС 50 мм и SLOPE плит берутся как `supplier_required_volume_m3`;
- расходные материалы временно берутся как предоставленный raw total;
- логистика и снабжение временно берётся как предоставленный raw total;
- технический надзор берётся как предоставленный fixed work total;
- заготовительно-складские расходы берутся как предоставленный fixed work total;
- `roof_work_coeff` является параметром проекта и может меняться.

## price_registry

У материальных строк есть `price_code`. Сейчас цены берутся из `input.json`.
Позже `price_code` можно связать с Google Sheets `price_registry`, не меняя смысловые формулы.

## Почему SLOPE плиты не считаются автоматически

Уклонные плиты зависят от схемы водоразделов, воронок, уклонов и раскладки производителя.
Для текущего MVP объёмы от поставщика фиксируются как ручной вход, чтобы не имитировать точность, которой пока нет.
