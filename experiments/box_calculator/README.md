# Box Calculator Experiment

Экспериментальный слой агрегации разделов коробки дома.

На текущем этапе реализован только безопасный блок распределения доставки арматуры/металла:

```text
recommended_metal_delivery_allocation
```

Он не меняет старые section totals и не добавляет доставку поверх legacy-строк разделов.

## Запуск теста

Из корня проекта:

```bash
../.venv/bin/python3 experiments/box_calculator/run_box_calculator.py experiments/box_calculator/cases/test_metal_delivery_allocation
```

## Правило доставки металла

- общий вес металла собирается по разделам коробки;
- машина считается кратно `capacity_kg`, сейчас 10 000 кг;
- количество машин: `ceil(total_box_metal_weight_kg / capacity_kg)`;
- первая машина назначается первому разделу с металлом;
- следующие машины назначаются разделу, на котором накопленный вес пересёк очередную границу 10 тонн.

## Важно

Старые калькуляторы разделов пока могут содержать legacy-строки доставки металла.
Поэтому allocation показывается отдельно и не добавляется к итогам.

Excel exporter позже должен заменить legacy delivery line на allocation line в нужном разделе.
