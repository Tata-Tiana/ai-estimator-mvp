# A5.1a — resolver_hints for AUTO_PROJECT P0 (before/after)

Дата: 2026-07-07. Только 24 P0 из inventory (A5.1). P1 list/nested,
reclassification_candidates, audit-статусы — не трогались.
`section_classifier`/`generic_candidate_extractor`/`resolver_engine` — не менялись.

## Что сделано

24 параметра были auto-flattened из `input.json` (без единого resolver_hint).
Каждый добавлен как явная запись в `EXPLICIT_PARAMETERS` с hints, основанными
на реальных кандидатах USV/TRC (не только на названии параметра).

## Тесты

213 (usv_strict_pdf_parser_v3) — не менялись, не запускались повторно (парсер
не трогался). `pdf_parser_pipeline`: 35 passed, 1 skipped — включая оба
generic guard-теста (bare project numbers, value_range ≥10×) на все 69
hints (45 старых + 24 новых).

## До / После (resolve_all по 24 P0)

| Проект | found (было) | found (стало) | missing |
|---|---|---|---|
| USV | 0/24 | **8/24** | 16 |
| TRC | 0/24 | **10/24** | 14 |
| Union (найдено хотя бы в одном) | 0/24 | **13/24 (54%)** | 11 |

## Found — примеры

| project | parameter | value | unit | confidence | needs_review |
|---|---|---|---|---|---|
| USV | main_formwork_area_m2 | 212.35 | m2 | 0.75 | True |
| USV | roof_area_level_1_m2 | 212.35 | m2 | 0.85 | True |
| USV | vent_wall_abutment_level_1_m | 24.65 | linear_m | 0.85 | False |
| USV | vent_channel_2_count | 24.0 | pcs | 0.85 | True |
| USV | parapet_masonry_volume_m3 | 30.4 | m3 | 0.6 | True |
| TRC | geotextile_laying_area_m2 | 189.28 | m2 | 0.85 | True |
| TRC | vent_channel_1_height_m | 4.9 | linear_m | 0.9 | True |
| TRC | parapet_length_level_1_m | 6.0 | linear_m | 0.6 | True |

## Missing — примеры и честные причины

| parameter | причина |
|---|---|
| main_wall_reinforcement_rows / 400 / 250_threads | Реальная эвиденция ("14-й ряд (армирование кладки)") типизирована `elevation_marker` — auxiliary-тип, resolve() исключает его до скоринга (A4.2.5.1). Это не пробел в hints, а структурное ограничение экстрактора. |
| trench_volume_m3 | Нет "ИТОГО"-строки с готовым объёмом траншей ни в USV, ни в TRC — калькулятор и так рассчитан на fallback через trench_routes. |
| vent_shaft_abutment_count / roof_aerators_count / gas_block_wall_holes_count | В обоих проектах не нашлось явной строки с этими количествами — возможно, отсутствуют в PDF, либо термины отличаются от использованных в hint. |
| slab_edge_perimeter_m / edge_insulation_height_m | Нет чистого кандидата с этим значением на floor_slab_2 страницах в этих двух проектах. |

## Известные ограничения (честно, не скрываю)

1. **level_1/level_2 и channel_1/channel_2 неразличимы generic-способом.** `roof_area_level_1_m2` и `roof_area_level_2_m2` (аналогично `parapet_length_level_*`, `vent_wall_abutment_level_*`, `vent_channel_1/2_height_m`) находят **один и тот же** кандидат — в PDF нет словесного маркера "уровень 1"/"уровень 2", только отметка высоты, которую нельзя использовать в context (это будет project-specific число, guard-тест такое отклонит). Оба параметра получают одно и то же значение; если бы в PDF было два разных числа — сработал бы conflict/needs_review. Это осознанный компромисс, не баг.
2. **`communications_length_m` (USV, 35.0 linear_m, needs_review=False)** — значение взято из огромного смешанного page_text-кандидата (искажённый текст генплана), конкретно совпало со строкой "Труба ф110 гофрированная 35 м/п" — это длина ОДНОГО типа трубы, не обязательно суммарная длина всех коммуникаций. Технически "found", но семантически сомнительно — стоит проверить человеком, хотя система сейчас не просит об этом (needs_review=False).
3. **`roof_area_level_1/2_m2` на TRC (21.28 m2)** — по-прежнему берётся из смешанного блока (`Площадькровли | 21,28м2 | 15,78м2 75,975м2`), в отличие от USV, где нашёлся чистый атомарный кандидат и значение поправилось на 212.35. Для TRC такого чистого кандидата нет — не удалось улучшить в рамках этого шага.

## Найденные и исправленные при проверке баги (в самих hints, до финализации)

- `main_wall_reinforcement_rows/400/250` изначально ловили несвязанный кандидат про арматуру плиты перекрытия (слово "армирование" слишком общее) — сужено до `кладк`+`ряд|нит`, затем ещё раз — до исключения "обкладка" (вентканалов), которое содержит "кладк" как подстроку.
- `roof_area_level_1/2_m2` изначально брали "294 м2" — площадь пароизоляции из того же смешанного блока, что и площадь кровли — добавлен `negative_context` на материалы пирога кровли, что дало правильный атомарный кандидат для USV.

Обе проблемы нашла и починила через прямую проверку `raw_text`, не полагаясь только на статус found/missing.
