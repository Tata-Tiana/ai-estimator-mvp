# Test manual excavation spec trench volume

Тестовый кейс для production-стандарта, где проектная спецификация уже даёт готовый объём траншей.

## Проверяемый приоритет

```text
if trench_volume_m3 is provided:
    trench_volume_total_m3 = trench_volume_m3
else:
    trench_volume_total_m3 = sum(route.length_m * route.depth_m * 0.4)
```

## Проверочный расчёт

- Доработка котлована: `330 * 0.08 = 26.4 м3`
- Готовый объём траншей: `18.29 м3`
- Ручная разработка всего: `26.4 + 18.29 = 44.69 м3`
- Песок в траншеи: `18.29 * 1.3 = 23.777 м3`

## Важно

- `trench_volume_source = spec_volume`.
- `trench_routes` не требуются, если есть готовый `trench_volume_m3`.
- Ручная разработка и песок в траншеи используют один и тот же `trench_volume_total_m3`.
