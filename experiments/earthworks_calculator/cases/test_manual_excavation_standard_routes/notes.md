# Test manual excavation standard routes

Тестовый кейс для production-стандарта ручной разработки грунта.

## Проверяемая формула

```text
manual_pit_volume_m3 = pit_area_m2 * 0.08
trench_route_volume_m3 = route_length_m * route_depth_m * 0.4
manual_excavation_total_m3 = manual_pit_volume_m3 + sum(trench_route_volume_m3)
```

## Проверочный расчёт

- Доработка котлована: `330 * 0.08 = 26.4 м3`
- К1: `10 * 1.2 * 0.4 = 4.8 м3`
- К2: `8 * 1.0 * 0.4 = 3.2 м3`
- ВК: `12 * 1.4 * 0.4 = 6.72 м3`
- ЭО: `5 * 0.7 * 0.4 = 1.4 м3`
- Траншеи всего: `16.12 м3`
- Ручная разработка всего: `42.52 м3`

## Важно

- `manual_excavation_quantity_for_estimate_m3` не используется и не требуется.
- `assumptions.manual_excavation_override` не используется и не требуется.
- `trench_width_m = 0.4` является системной настройкой для текущего стандарта.
- Длины и глубины трасс являются проектными данными из спецификации/чертежа.
