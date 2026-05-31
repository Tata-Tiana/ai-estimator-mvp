# MVP Scope

Дата актуализации: `2026-05-20`.

## Цель MVP

MVP должен показать, что проектную документацию частного дома можно превратить в проверяемые входные данные для сметы, а затем посчитать хотя бы один раздел сметы детерминированным кодом.

## Что входит в MVP

1. PDF-парсинг проекта:
   - извлечение текста;
   - извлечение таблиц;
   - сохранение артефактов по каждому дому.

2. AI-карточка проекта:
   - общие параметры дома;
   - фундамент;
   - стены и перегородки;
   - перекрытия/покрытие;
   - кровля;
   - вентиляция/дымоходы;
   - материалы;
   - missing data и warnings.

3. Расчётные экспериментальные модули:
   - раздел "Земляные работы";
   - раздел "Устройство фундаментной плиты";
   - блок "Гидроизоляция фундаментной плиты";
   - раздел "Внешние и внутренние несущие стены, перемычки";
   - расчёт объёмов;
   - серые внутренние строки материалов и работ;
   - внутренние итоги раздела;
   - сравнение с эталонными сметами.

4. Организация кейсов:
   - отдельная папка на дом;
   - `input.json`;
   - `expected.json`;
   - `notes.md`;
   - агрегированный запуск всех кейсов.

5. Подготовка к УНИКМА:
   - тест API;
   - понимание формата номенклатуры и прайса;
   - черновой material matching.

## Что пока не входит в MVP

- клиентская цена;
- рентабельность 1.32;
- НР/СП/ТН;
- полноценная коммерческая смета;
- автоматическое принятие спорных AI-выводов без ручной проверки;
- автоматический матчинг всех материалов с УНИКМА;
- UI;
- production backend.

## Текущая граница расчёта

Сейчас расчётный слой считает только внутреннюю себестоимость:

```text
internal_materials_total
internal_works_total
internal_section_total
```

Проверенные калькуляторы и кейсы:

- `experiments/earthworks_calculator/`
  - `usv_yusupovo_village` — эталонный, разобран с Еленой;
  - `horoshevka_14` — повторение сметы, с явными overrides.
- `experiments/foundation_slab_calculator/`
  - `test_foundation_slab` — раздел фундаментной плиты, сверен со скрином Excel.
- `experiments/waterproofing_calculator/`
  - `test_waterproofing_foundation_slab` — гидроизоляция и утепление бортов плит, сверено со скрином Excel.
- `experiments/load_bearing_walls_lintels_calculator/`
  - `test_load_bearing_walls_lintels` — несущие стены и перемычки, с raw/display итогами из-за округлений Excel.
- `experiments/floor_slab_1_calculator/`
  - `test_floor_slab_1` — плита перекрытия 1-го этажа с балками.
- `experiments/floor_slab_2_calculator/`
  - `test_floor_slab_2` — плита перекрытия 2-го этажа без балок.
- `experiments/flat_roof_calculator/`
  - `test_flat_roof_usv` — плоская кровля, без временной двери как case-specific строки.
- `experiments/schiedel_vent_channels_calculator/`
  - `test_schiedel_vent_channels_usv` — вентиляционные каналы Schiedel.

Слой цен для MVP:

- `experiments/pricing/`;
- `output/price_registry_filled_v3.xlsx`;
- единый `price_code` в готовых калькуляторах;
- текущий расчётный режим — `locked_case_prices`;
- будущий режим — `price_registry_with_fallback`, с приоритетом `project_price_overrides -> price_registry -> input fallback`.

## Принцип развития

Каждый новый раздел сметы сначала делается как экспериментальный калькулятор в `experiments/`, затем обкатывается на нескольких кейсах, и только после этого может переноситься в `app/estimator/`.
