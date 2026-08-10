# P5. Новый production contract для плит перекрытия

Дата: 2026-08-10

## Решение

Плиты больше не считаются как два фиксированных раздела:
- `floor_slab_1`;
- `floor_slab_2`.

Production-модель после P5:

```text
проект -> список физических плит -> один общий калькулятор запускается по каждой плите
```

Одна физическая плита проекта = одна `slab_zone`.

Это может быть:
- плита перекрытия 1 этажа;
- плита кухни/гостиной;
- плита второго света;
- плита лестницы;
- кровельная ж/б плита;
- любая другая плита, если проектировщик дал ее как отдельную конструкцию/раздел.

Нельзя привязывать production-логику к номеру этажа. Номер этажа, отметка, марка плиты и название листа
являются контекстом, а не типом калькулятора.

## Новая верхнеуровневая структура extraction JSON

Рабочая структура:

```yaml
sections:
  floor_slabs:
    section_code: floor_slabs
    slab_zones:
      - zone_id: string
        display_name: string
        source_level: string | null
        slab_mark: string | null
        slab_kind: residential_floor | roof_slab | stair_slab | other | unknown
        include_in_estimate: true
        source_refs: []
        status: found | needs_review | missing
        confidence: number
        notes: string | null
        concrete: {}
        formwork: {}
        insulation: {}
        beams: {}
        rebar_items: []
        additional_items: []
        manual_inputs: {}
```

`floor_slabs` заменяет production-использование старых `floor_slab_1` и `floor_slab_2`.

## Идентификация зоны

Каждая плита должна иметь стабильный `zone_id`.

Правило:
- если в PDF есть марка плиты, использовать ее как основу: `pm1`, `pm2`, `fp1`, `slab_b1`;
- если марки нет, использовать нейтральный контекст: `slab_level_3_480`, `roof_slab_main`;
- `zone_id` не должен содержать имя проекта, адрес или числа сметы;
- `zone_id` нужен только для связи строк внутри JSON и workbook.

Обязательные поля контекста:

```yaml
zone_id:
display_name:
source_level:
slab_mark:
source_refs:
```

Примеры `display_name`:
- `Плита ПМ1`;
- `Плита покрытия стен второго света`;
- `Ж/Б монолитная плита перекрытия`;
- `Плита лестницы`.

## Бетон

```yaml
concrete:
  slab_volume_m3:
    value:
    unit: m3
    source_ref:
    status:
    confidence:
    notes:
  beam_volume_m3:
    value:
    unit: m3
    source_rule: explicit_total | auto_sum_beam_items | missing
    status:
    confidence:
    notes:
  total_with_beams_m3:
    value:
    unit: m3
    source_rule: explicit_pdf_total | diagnostic_only
    status:
    confidence:
    notes:
```

Правила:
- бетон плиты и бетон балок не смешивать;
- если PDF дает отдельную строку бетона плиты, она идет в `slab_volume_m3`;
- если PDF дает балки построчно, они идут в `beams.items[].concrete_volume_m3`;
- `beam_volume_m3` можно считать автосуммой из `beams.items[]`;
- если PDF дает общий итог "плита + балки", это не заменяет отдельные поля, а сохраняется как контроль;
- если общего итога нет, модель не должна придумывать его как PDF-строку.

## Опалубка

```yaml
formwork:
  under_slab_area_m2:
    value:
    status:
    confidence:
    notes:
  edge_area_m2:
    value:
    status:
    confidence:
    notes:
  edge_and_beam_combined_area_m2:
    value:
    status:
    confidence:
    notes:
  beams_side_area_m2:
    value:
    source_rule: explicit_total | auto_sum_beam_items | missing
    status:
    confidence:
    notes:
  beams_bottom_area_m2:
    value:
    status:
    confidence:
    notes:
```

Правила:
- нижняя опалубка плиты (`under_slab_area_m2`) и опалубка торца (`edge_area_m2`) разные вещи;
- площадь опалубки торца не равна объему ЭППС;
- если проект дает "торец плиты + балки вместе", сохранять в `edge_and_beam_combined_area_m2` и
  ставить `needs_review`, пока разделить нельзя;
- нижняя опалубка балок (`beams_bottom_area_m2`) не выводится автоматически из длины балок, если проект
  не дает явную площадь.

## Утепление

Утепление должно храниться не как один scalar, а как список проектных строк/компонентов.

```yaml
insulation:
  eps_items:
    - role: slab_bottom | slab_edge | beam_edge | lintel_edge | combined_bottom_and_edge | unknown
      material_name:
      thickness_mm:
      volume_m3:
      area_m2:
      length_m:
      height_m:
      source_ref:
      source_phrase:
      status:
      confidence:
      notes:
```

Правила:
- "низ плиты", "торец плиты", "торец балок", "торец перемычек" не смешивать;
- "торец плиты" и "борт плиты" считать одним смыслом;
- если в PDF есть объем ЭППС 100 мм, площадь материала можно вычислить как `volume_m3 / 0.1`;
- если в PDF есть объем ЭППС 50 мм, площадь материала можно вычислить как `volume_m3 / 0.05`;
- вычисленная площадь всегда идет со статусом `needs_review` и понятной заметкой;
- если PDF дает объединенную строку "торец + низ", это `combined_bottom_and_edge`, а не две выдуманные
  строки;
- если длина работ по торцу дана отдельно в м.п., она сохраняется как `length_m`;
- если длина работ не дана, нельзя выводить ее из объема без отдельного утвержденного правила.

## Балки

```yaml
beams:
  items:
    - beam_id:
      mark:
      length_m:
      width_m:
      height_m:
      count:
      concrete_volume_m3:
      formwork_area_m2:
      bottom_formwork_area_m2:
      insulated_length_m:
      insulation_area_m2:
      source_ref:
      status:
      confidence:
      notes:
```

Правила:
- балки являются частью конкретной `slab_zone`;
- если PDF дает балки по маркам, сохранять построчно;
- если PDF объединяет несколько балок в одну строку, сохранять как одну строку с `needs_review`;
- ширина балки не обязательна для ставки бетонирования, если production-решение считает работу по м.п.;
- длина балки не равна длине утепляемой части балки;
- утепление балок нужно брать только из явной строки/указания проекта.

## Арматура

```yaml
rebar_items:
  - component: slab | beam | additional | unknown
    steel_class:
    diameter_mm:
    spec_length_m:
    kg_per_meter:
    source_ref:
    status:
    confidence:
    notes:
```

Правила:
- арматура плиты и арматура балок могут лежать на одном листе, но должны сохраняться как строки одной
  зоны;
- primary unit из PDF обычно `м.п.`;
- вес считается калькулятором по `kg_per_meter`, если он нужен;
- не использовать `weight_kg` как основной production input, если PDF дал длину в м.п.

## Дополнительные элементы

```yaml
additional_items:
  - item_type:
    name:
    quantity:
    unit:
    source_ref:
    status:
    confidence:
    notes:
```

Сюда попадают редкие проектные вещи:
- закладные детали;
- уникальные листы/доборы;
- специальные элементы, которые есть не во всех проектах.

Они не должны становиться обязательными строками для каждой плиты.

## Ручные поля на плиту

Ручные поля должны быть привязаны к конкретной `slab_zone`, а не к старому разделу `floor_slab_1`.

```yaml
manual_inputs:
  formwork_rebar_crane_shifts:
  rebar_metal_delivery_trucks:
  concrete_pump_shifts:
  technical_supervision_amount:
  formwork_rental_supplier_quote_total:
```

Правила:
- кран, насос, доставка металла и технадзор считаются per-slab/per-pour, а не общим пулом на все плиты;
- если значения нет в проекте, оно должно появиться в Google workbook как ручная строка;
- технадзор можно оставлять 0 по умолчанию, но он должен быть видимым для проверки.

## Google workbook после P5

Лист `01_Проверка проекта` должен показывать плиты динамически:

```text
Плиты перекрытия / покрытия
  Плита ПМ1
    бетон
    опалубка
    утепление
    балки
    арматура
    ручные поля
  Плита ПМ2
    ...
  Плита лестницы
    ...
```

Строки больше не должны называться так, будто есть только "перекрытие 1 этажа" и "перекрытие 2 этажа".

Цвета:
- найдено уверенно = зеленый;
- найдено, но требует проверки / вычислено = оранжевый;
- обязательно, но не найдено = красный;
- optional / не применяется = нейтральный.

## Adapter после P5

Adapter должен:
- читать только новую `floor_slabs.slab_zones[]`;
- запускать общий калькулятор по каждой включенной зоне;
- не читать старые `floor_slab_1_*` / `floor_slab_2_*` scalar-поля;
- не создавать `[combined]` fallback;
- падать readiness blocker, если зона не готова к расчету.

### Известный долг в самом калькуляторе — убрать вместе с adapter (найдено 2026-08-10)

`experiments/floor_slab_1_calculator/floor_slab_calculator.py`, функции `calculate_rebar_item()`
(строки ~92-105) и `calculate_rebar_items_pooled()` (строки ~166-180) внутри общего движка
`calculate_floor_slab_pour()` жёстко требуют:

```python
if item.get("component") != "floor_slab_1":
    raise ValueError(...)
if int(item.get("floor", 0)) != 1:
    raise ValueError(...)
```

Это буквально требование "арматура обязана называться component='floor_slab_1', floor=1" —
леftover с тех пор, когда эта функция считала только плиту 1 этажа (см. собственный docstring
`calculate_floor_slab_pour()`, строки ~926-931: "a real leftover... needs generalizing once P2
makes this a genuinely pour-agnostic N-pour engine"). P2 (N-pour orchestration) уже построен, но
эту конкретную проверку не трогал. Сегодня `floor_slab_2_calculator/calculator.py`'s wrapper
обходит это, подставляя фиктивные `component="floor_slab_1"`/`floor=1` в каждую строку арматуры
перед вызовом движка — работает, но это заглушка, а не реальная логика, и именно то, что нужно
убрать в рамках зачистки "как будто написали заново".

Новая схема `floor_slab_rebar_items` не имеет поля `floor` вообще — зону однозначно определяет
`zone_id`. Когда adapter будет писаться под `floor_slabs`, нужно:
- убрать обе проверки `component`/`floor` из `calculate_rebar_item()`/`calculate_rebar_items_pooled()`
  (они ничего не проверяют по сути, только требуют конкретные строковые/числовые литералы);
- убедиться, что ничего ниже по движку не читает `item["floor"]`/`item["component"]` для реальной
  логики (проверено 2026-08-10: не читает, значение используется только для этой равенство-проверки
  и попадает в `source_payload`/output как есть — безопасно удалить);
- удалить фиктивную подстановку `component="floor_slab_1"`/`floor=1` из
  `floor_slab_2_calculator/calculator.py`'s translation wrapper, когда она перестанет быть нужна.

Не делать это раньше adapter-этапа — вне контекста N-pour adapter-а это старые 19+ регрессионных
кейсов `floor_slab_1_calculator`, которые сейчас проходят именно с этими литералами; трогать движок
нужно вместе с переводом adapter-а на `zone_id`, одним шагом, с перепроверкой регрессии.

## Старые поля

Старые поля после P5:
- можно оставить в архивных тестах;
- можно использовать в regression fixture до переписывания тестов;
- нельзя использовать в production parser upload pack;
- нельзя использовать как fallback в workbook или adapter.

## Первый практический шаг после этого документа

Начать с parser-side:

1. Создать новую секцию `floor_slabs` в `calculator_targets_compact.json`.
2. Перенести активные aliases из `floor_slab_1`/`floor_slab_2` в новую логику зон.
3. Обновить extraction schema, чтобы `slab_zones[]` была явной структурой.
4. Обновить prompt: модель должна сначала найти все физические плиты, потом раскладывать строки по зонам.
5. После parser-side правок пересобрать upload zip и сделать новый extraction.

Только после этого переходить к workbook/adapters.
