# A4.2.5 Smoke Report — Фильтрация мусорных кандидатов

**Дата:** 2026-07-05  
**Ветка:** feature/parser-resolver-layer

---

## Что сделано

### Изменения в коде

**`generic_candidate_extractor.py`**
1. **Elevation pre-check перед gate**: `parse_quantities()` теперь вызывается до проверки `_has_any_quantity`. Elevation-значения вида `+3,250` не имеют суффикса единиц (м²/м³/п.м), поэтому `_has_any_quantity` возвращал False и они выбрасывались. Теперь elevation-значения перехватываются до gate и создают `elevation_marker`.

2. **`_has_useful_primary_quantity` — исключение `mm`**: `parse_quantities('К1 труба Ø110 мм')` возвращает и `('diameter', '110', 'mm')` и `('length', '110', 'mm')` — одно значение парсится дважды. Предыдущая версия видела `kind='length'` и считала это "полезной первичной величиной", создавая `route_summary` вместо `diameter_spec`. Теперь `normalized_unit in ('mm', 'мм')` исключается — диаметры в мм не считаются маршрутной величиной.

**`tests/test_evidence_layer.py`**
3. **Фикс mixed-page test**: `_make_table()` получил параметр `table_title`. Тест `test_table_override_when_page_known_but_table_strongly_disagrees` передаёт `table_title='Спецификация к фундаментной плите'` — иначе `infer_table_context_title` падает обратно на `logical_sheet_title` страницы (`'Схема гидроизоляции'`) и классификатор возвращает `waterproofing` вместо `foundation_slab`.

---

## Тесты: 204/204 ✓

Все 4 падавших теста исправлены:
- `test_elevation_value_creates_elevation_marker_not_ordinary` ✓
- `test_elevation_marker_has_low_confidence` ✓
- `test_diameter_only_route_becomes_diameter_spec` ✓
- `test_table_override_when_page_known_but_table_strongly_disagrees` ✓

---

## Smoke: USV

| Метрика | Значение |
|---|---|
| Evidence | 976 (859 table_row) |
| Кандидатов итого | **168** (было 151 до A4.2.5) |

### Типы кандидатов

| Тип | Кол-во | Доля |
|---|---|---|
| material_quantity | 74 | 44% |
| route_summary | 37 | 22% |
| **elevation_marker** (новый) | **37** | **22%** |
| pipe_item | 10 | 6% |
| table_quantity_row | 7 | 4% |
| **diameter_spec** (новый) | **2** | **1%** |
| pipe_piece_qty | 1 | 1% |

### Section source

| Источник | Кол-во |
|---|---|
| page | 135 (80%) |
| table | 16 (10%) |
| **table_override** | **9** (5%) |
| unknown | 8 (5%) |

### Section code

| Раздел | Кол-во |
|---|---|
| flat_roof | 40 |
| floor_slab_unknown | 38 |
| foundation_slab | 28 |
| load_bearing_walls_lintels | 20 |
| earthworks | 13 |
| waterproofing | 12 |
| schiedel_vent_channels | 9 |
| unknown | 8 |

---

## Smoke: TRC

| Метрика | Значение |
|---|---|
| Evidence | 2209 (2055 table_row) |
| Кандидатов итого | **511** (было 340 до A4.2.5) |

### Типы кандидатов

| Тип | Кол-во | Доля |
|---|---|---|
| **elevation_marker** (новый) | **192** | **38%** |
| material_quantity | 178 | 35% |
| route_summary | 44 | 9% |
| label_value_quantity | 37 | 7% |
| table_quantity_row | 24 | 5% |
| pipe_item | 22 | 4% |
| diameter_spec (новый) | 8 | 2% |
| pipe_piece_qty | 5 | 1% |
| unknown_relevant_quantity | 1 | 0% |

### Section source

| Источник | Кол-во |
|---|---|
| page | 406 (79%) |
| **unknown** | **97** (19%) |
| table_override | 6 (1%) |
| table | 2 (0.4%) |

### Section code (топ-10)

| Раздел | Кол-во |
|---|---|
| floor_slab_1 | 109 |
| unknown | 97 |
| foundation_slab | 58 |
| load_bearing_walls_lintels | 56 |
| floor_slab_2 | 46 |
| earthworks | 45 |
| schiedel_vent_channels | 39 |
| waterproofing | 24 |
| floor_slab_unknown | 20 |
| flat_roof | 17 |

---

## Наблюдения

**elevation_marker доминирует в TRC (38%)** — многоэтажный объект с большим количеством отметок в таблицах спецификаций. Это ожидаемо и правильно: маркеры не попадают в resolver как первичные величины (confidence 0.20).

**97 unknown в TRC (19%)** — страницы, не распознанные page-классификатором. Возможные причины: архитектурные/генеральные листы без строительных сигналов. Требует отдельного аудита в A4.2.8.

**table_override: USV=9, TRC=6** — работает. Срабатывает когда `table_title` у таблицы указывает на другой раздел, чем страница. На TRC данных только 6 таблиц имеют явный `table_title` отличный от страницы.

**diameter_spec: USV=2, TRC=8** — корректно изолированы трубные спецификации без маршрутной длины (только Ø+мм).

---

## Следующие шаги

- **A4.2.6**: row-level классификация (сигналы К1, LOGICROOF, Schiedel в отдельных строках)
- **A4.2.8**: аудит 97 unknown-кандидатов TRC — расширить page-классификатор или добавить row-level сигналы
- **A5**: сводная таблица для проверки покрытия по всем 8 разделам
