# P5. Инвентаризация плит перекрытия перед чистой схемой

Дата: 2026-08-10

## Главное решение

P5 делается как clean-slate production path.

Не поддерживаем старый формат как fallback:
- `floor_slab_1_*` scalar targets;
- `floor_slab_2_*` scalar targets;
- раздельную логику "1 этаж / 2 этаж" как источник истины;
- тихие автоподстановки в старые поля, если новой структуры нет.

Если после P5 в extraction JSON нет новой повторяемой структуры по плитам, pipeline должен остановиться с понятным blocker, а не пытаться собрать смету по старым полям.

## Что сейчас найдено

Система пока не готова к clean-slate P5. Старые поля сидят в четырех местах:

1. parser targets и aliases;
2. section contracts;
3. Google review workbook builder;
4. review-to-calculator adapters.

Калькулятор уже частично двигается к общей логике, но входной слой еще не приведен к одному production contract.

## Parser targets

В `experiments/chat_extraction_poc/data/calculator_targets_compact.json` активны старые цели.

### Старые цели floor_slab_1

- `floor_slab_1_kind`
- `floor_slab_1_concrete_volume`
- `floor_slab_1_slab_thickness`
- `floor_slab_1_slab_edge_perimeter`
- `floor_slab_1_under_slab_formwork_area`
- `floor_slab_1_edge_formwork_area`
- `floor_slab_1_edge_and_beam_formwork_area_combined`
- `floor_slab_1_beams_formwork_area`
- `floor_slab_1_beams_bottom_formwork_area`
- `floor_slab_1_beams_concrete_volume`
- `floor_slab_1_edge_eps_work_length`
- `floor_slab_1_beams_eps_work_length`
- `floor_slab_1_edge_insulation_height`
- `floor_slab_1_edge_eps_material_area`
- `floor_slab_1_beams_eps_material_area`
- `floor_slab_1_bottom_eps_work_area`
- `floor_slab_1_eps100_volume`

### Старые цели floor_slab_2

- `floor_slab_2_kind`
- `floor_slab_2_concrete_volume`
- `floor_slab_2_slab_edge_perimeter`
- `floor_slab_2_main_formwork_area`
- `floor_slab_2_edge_formwork_area`
- `floor_slab_2_beams_formwork_area`
- `floor_slab_2_beams_bottom_formwork_area`
- `floor_slab_2_beams_concrete_volume`
- `floor_slab_2_edge_insulation_height`
- `floor_slab_2_beams_eps_work_length`
- `floor_slab_2_beams_eps_material_area`
- `floor_slab_2_bottom_eps_work_area`
- `floor_slab_2_slab_area`

Вывод: parser все еще просит модель искать старые одиночные поля. Для P5 их надо заменить новой структурой, а не расширять.

## Aliases

В `target_aliases_ru.yaml` тоже активны старые ключи `floor_slab_1_*` и `floor_slab_2_*`.

Также есть раздельные repeated groups:
- `floor_slab_1_rebar_items`;
- `floor_slab_2_rebar_items`;
- `beam_items`;
- `floor_slab_2_beam_items`;
- `additional_concrete_items`;
- `beam_table_controls`.

Вывод: aliases сейчас направляют модель в две старые плиты. Для P5 нужен общий словарь под repeated zones, где одна плита проекта является одной зоной/плитой, а не жестко "первый этаж" или "второй этаж".

## Section contracts

### floor_slab_1

`experiments/full_estimate_review_pipeline/sections/floor_slab_1/section_contract.yaml`

Уже есть `slab_zones`, но contract все еще содержит много старых scalar-параметров:
- общий бетон;
- толщина;
- периметр;
- опалубка низа;
- опалубка торца;
- опалубка торца + балок вместе;
- опалубка балок;
- бетон балок;
- длины утепления торца плиты и балок;
- площадь материала ЭППС;
- площадь нижнего утепления;
- общий объем ЭППС 100 мм.

То есть `slab_zones` сейчас не является единственным production input. Это смешанный режим.

### floor_slab_2

`experiments/full_estimate_review_pipeline/sections/floor_slab_2/section_contract.yaml`

Есть `slab_zones`, но `calculator_input_path` у него пустой. Основные входы по-прежнему scalar:
- опалубка;
- бетон;
- балки;
- периметр;
- утепление;
- площадь плиты для контроля.

Вывод: контракты надо не "свести косметически", а заменить production contract на общий контракт плит.

## Workbook builder

`experiments/full_estimate_review_pipeline/populate_review_workbook_from_extraction.py`

Найдены старые функции и правила:
- `floor_slab_1_alternative_scalar(...)`;
- `floor_slab_2_alternative_scalar(...)`;
- автосуммы в старые target_code;
- вычисление старых строк из `slab_zones` и `beam_items`;
- отображение "Не требуется (есть в slab_zones)" для старых строк.

Это полезные идеи, но не production P5.

Для P5 workbook должен строить лист 01 из новой структуры плит:
- каждая найденная плита отдельным блоком;
- внутри блока бетон, опалубка, утепление, балки, арматура, ручные строки;
- вычисленные строки отмечаются как "Проверьте", но не записываются в старые scalar targets;
- если данные не позволяют разделить плиту/балки/низ/торец, это отдельная строка проверки или blocker.

## Review-to-calculator adapters

Найдены текущие адаптеры:
- `review_to_calculator/sections/floor_slab_1/build_input.py`;
- `review_to_calculator/sections/floor_slab_2/build_input.py`.

Проблема:
- адаптеры все еще читают старые scalar keys;
- есть логика `[combined] if not safely attributable`;
- есть fallback/unsplit pour;
- часть общих расходов живет по старой схеме;
- floor_slab_2 до конца не живет от `slab_zones`.

Для P5 такие fallback-ветки надо убрать из production. Если зона не атрибутируется, это не "combined fallback", а проверочный blocker.

## Как должна выглядеть новая production-структура

Рабочее название:

```yaml
floor_slabs:
  slab_zones:
    - zone_id:
      section_title:
      source_level:
      slab_mark:
      kind:
      source_refs:
      concrete:
        slab_volume_m3:
        additional_concrete_items:
        beam_items:
      formwork:
        under_slab_area_m2:
        edge_area_m2:
        edge_and_beam_combined_area_m2:
        beams_bottom_area_m2:
      insulation:
        eps_items:
          - role:
            thickness_mm:
            volume_m3:
            area_m2:
            length_m:
            source_phrase:
            needs_review:
      rebar_items:
      manual_inputs:
      status:
      confidence:
      notes:
```

Смысл:
- parser извлекает не "плиту 1 этажа" и "плиту 2 этажа", а все плиты перекрытия/покрытия как повторяемые зоны;
- каждая зона сама несет свои данные по бетону, опалубке, утеплению, балкам и арматуре;
- calculator запускается столько раз, сколько зон включено в смету;
- цены и defaults подтягиваются по единому slab contract.

## Что надо сделать первым

1. Зафиксировать новую schema для `floor_slabs.slab_zones[]`.
2. Переписать `calculator_targets_compact.json` под новую структуру.
3. Переписать `target_aliases_ru.yaml`: убрать active старые `floor_slab_1_*` / `floor_slab_2_*`, добавить aliases под зоны, балки, ЭППС, опалубку и арматуру внутри зоны.
4. Обновить extraction schema и prompt: модель должна возвращать repeated slab zones, а не scalar-поля двух этажей.
5. Переписать section contract: один общий production contract для плит.
6. Переписать Google workbook builder: лист 01 должен строиться из зон.
7. Переписать adapter review -> calculator input: никаких combined fallback.
8. После этого пересобрать zip pack и делать новый extraction. Старые JSON не должны считаться валидным input для P5.

## Что нельзя делать в P5

- Нельзя оставлять старые scalar поля как production fallback.
- Нельзя делать "если не нашли новую структуру, возьмем старые floor_slab_1/floor_slab_2".
- Нельзя подтаскивать правила под АРК, ТРЦ или ЮСВ.
- Нельзя считать отсутствие зоны нормой.
- Нельзя молча суммировать бетон плиты и балки, если в проекте они даны разными сущностями.
- Нельзя терять компоненты утепления: низ, торец плиты, торец балок, перемычки должны быть отдельными ролями, даже если потом часть из них не участвует в расчете.

## Короткий вывод

Путь правильный, но объем работы больше, чем "слить два калькулятора".

Сейчас самый старый слой не калькулятор, а parser/contract/workbook. Если их не переписать, новый калькулятор будет получать старую кашу из scalar-полей и зон, а ошибки будут всплывать уже в финальной смете.

P5 надо начинать с новой extraction/schema/contract структуры, потом workbook, потом adapter/calculator run.
