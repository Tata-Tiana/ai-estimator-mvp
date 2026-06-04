# Project Notes

Дата актуализации: `2026-06-04`.

## Последняя расчётная контрольная точка

```text
branch: feature/ai-project-card
commit: см. последний коммит live-pricing в `git log`
```

Последняя рабочая цепочка проекта перед `box_calculator`:

```text
pdf_parser_pipeline -> input_builder -> calculation_runner
```

Рабочий путь подготовки параметров из PDF:

```text
experiments/pdf_parser_pipeline/
```

Более ранний `experiments/review_sheet_builder/` удалён как промежуточный эксперимент, чтобы не путаться в двух похожих контурах.

Слой сборки inputs:

```text
experiments/input_builder/
```

Demo fallback case:

```text
experiments/input_builder/cases/mvp_usv_demo_fallback/
experiments/input_builder/output/mvp_usv_demo_fallback/
```

Demo runner расчётов:

```text
experiments/calculation_runner/
```

Текущий demo-run:

```text
mode = demo_with_template_fallback
sections_completed = 8
sections_failed = 0
grand_total = 12 271 194
```

Это не production-расчёт и не финальная смета. Следующий слой — `box_calculator`.

Аудит missing/manual параметров и pack для созвона с Еленой:

```text
experiments/parameter_audit/
experiments/parameter_audit/output/mvp_usv_demo/elena_parameter_review_pack.xlsx
experiments/parameter_audit/output/mvp_usv_demo/elena_parameter_review_agenda.md
```

Текущая классификация 287 missing/manual параметров:

```text
AUTO_PROJECT = 140
AUTO_CALCULATED = 81
DEFAULT_VALUE = 26
PRICE_DATABASE = 7
MANUAL_REQUIRED = 33
```

Review-pack нужен для созвона с Еленой. Он не внедряет изменения в pipeline, а помогает подтвердить:

- какие параметры искать в проекте/PDF;
- какие считать автоматически;
- какие унести в defaults/material catalog;
- какие брать из price_registry;
- какие оставить ручными решениями сметчика.

В каждой строке pack есть пояснение, где параметр используется в смете и какая формула калькулятора от него зависит.

Новые стандарты фундаментной плиты после созвонов с Еленой:

```text
experiments/foundation_slab_calculator/
docs/standard_input_contract.md
docs/report_thermal_inserts_refactor.md
docs/report_foundation_slab_formwork_refactor.md
```

Опалубка бортов:

```text
formwork_calc_method = "spec_area"
slab_side_formwork_area_m2 = готовая площадь из спецификации
```

Термовставки:

```text
thermal_insert_mode = "standard_50_100"
```

Старые режимы `legacy_perimeter_height` и `legacy` сохранены только для старого эталонного кейса `test_foundation_slab`.

Проверочные кейсы:

```text
test_foundation_slab -> 229 ok / 0 mismatch
test_foundation_slab_thermal_inserts_standard -> 41 ok / 0 mismatch
test_foundation_slab_formwork_spec_area -> 25 ok / 0 mismatch
```

TODO отдельной задачей: обновить `pdf_parser_pipeline/section_schema.py`, чтобы Елена видела `slab_side_formwork_area_m2` и новые параметры термовставок как актуальный contract, а legacy-поля не попадали в ручной ввод новых проектов.

## Главные договорённости

- AI не считает смету, а помогает достать входные параметры.
- Расчёты делаются детерминированным Python-кодом.
- Любое отличие сметного количества от формульного расчёта фиксируется явно через overrides и notes.
- Для каждого дома должны быть отдельные проектные папки.
- В готовых калькуляторах используется один идентификатор цены: `price_code`.
- Старый режим расчёта остаётся `locked_case_prices`; цены берутся из inputs кейса.
- Будущий режим цен: `project_price_overrides -> price_registry -> input fallback`.
- `data/output` больше не считается удобной основной структурой для новых PDF/AI экспериментов.

## Имена проектных папок

Используем короткие латинские slug-имена:

- `horoshevka_14`
- `usv_yusupovo_village`

Для PDF-проектов, которые состоят из двух файлов:

- `kr1_below_floor` — ниже пола, фундаментная часть;
- `kr2_above_floor` — выше пола, стены/кровля/надземная часть.

## Где искать Хорошевку 14

PDF:

```text
experiments/pdf_tests/projects/horoshevka_14/
```

AI-карточка:

```text
experiments/ai_tests/projects/horoshevka_14/
```

Кейс земляных работ:

```text
experiments/earthworks_calculator/cases/horoshevka_14/
```

PDF/AI и расчётные материалы по фундаментной плите:

```text
experiments/meeting_analysis/input/2026-05-08_foundation_slab/
data/output/meeting_analysis/2026-05-08_1125_foundation_slab/
experiments/foundation_slab_calculator/
experiments/waterproofing_calculator/
experiments/load_bearing_walls_lintels_calculator/
experiments/floor_slab_1_calculator/
experiments/floor_slab_2_calculator/
experiments/flat_roof_calculator/
experiments/schiedel_vent_channels_calculator/
experiments/pricing/
experiments/input_builder/
experiments/calculation_runner/
```

PDF/AI и материалы по плоской кровле:

```text
experiments/meeting_analysis/input/2026-05-22_flat_roof/
data/output/meeting_analysis/2026-05-22_1103_flat_roof/
docs/report_flat_roof_calculator.md
```

Калькулятор плоской кровли создан как экспериментальный deterministic calculator. Итог сходится с серой зоной Excel за минусом временной двери ДН-1.

Материалы для будущего раздела ростверкового фундамента:

```text
experiments/meeting_analysis/input/2026-05-26_grillage_foundation/
```

Это raw input по разделу "Устройство ростверкового фундамента"; отдельный docs-отчёт по созвону не создаётся.

## Где искать price_registry и pricing-layer

```text
output/price_registry_filled_v3.xlsx
output/price_registry_mapping_report_v3.md
experiments/pricing/
experiments/pricing/output/price_registry_validation_report.md
experiments/pricing/output/required_codes_coverage_report.md
```

Состояние покрытия:

```text
required unique price_code = 81
found in price_registry = 18
found in rows_to_add = 63
missing completely = 0
```

## Где искать ЮСВ

Кейс земляных работ:

```text
experiments/earthworks_calculator/cases/usv_yusupovo_village/
```

## Статусы кейсов

В каждом `input.json` расчётного кейса есть:

```json
"case_meta": {
  "validated_with_elena": true,
  "confidence": "high"
}
```

И:

```json
"assumptions": {
  "manual_excavation_override": true,
  "sand_override": false,
  "geotextile_override": false
}
```

Это нужно, чтобы через несколько кейсов было видно, где настоящее правило, а где повторение конкретной сметы.

## Текущие результаты земляных работ

```text
horoshevka_14 -> ok (76/76), итог 559364
usv_yusupovo_village -> ok (100/100), итог 805020
```

Команда:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_all_cases.py
```

## Текущие результаты фундаментной плиты

```text
test_foundation_slab -> ok (205/205)
internal_materials_total = 1454675
internal_works_total = 1083650
internal_section_total = 2538325
```

Команда:

```bash
../.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab
```

Важное:

- клиентская часть не считается;
- пиломатериал считается как `formwork_area_m2 * 0.05`, без коэффициента `1.5`;
- PLANTERBAND считается как `membrane_rolls * 4`;
- доставка металла остаётся manual/fixed, но есть suggested trucks по правилу 10 тонн.

## Текущие результаты гидроизоляции фундаментной плиты

```text
test_waterproofing_foundation_slab -> ok (54/54)
waterproofing_base_subtotal = 48777
internal_materials_total = 33961
internal_works_total = 17255
internal_section_total = 51216
```

Команда:

```bash
../.venv/bin/python3 experiments/waterproofing_calculator/run_waterproofing_calc.py experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab
```

Блок сверен со скрином Excel: все видимые строки и итоги совпали.

## Текущие результаты несущих стен и перемычек

```text
test_load_bearing_walls_lintels -> ok
internal_materials_total_raw = 1550654.431
internal_materials_total = 1550654
internal_works_total_raw = 1121449.0
internal_works_total = 1121449
internal_section_total_raw = 2672103.431
internal_section_total = 2672103
```

Команда:

```bash
../.venv/bin/python3 experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels
```

Важное:

- клиентская часть не считается;
- Excel отображает строки округлёнными, но итог считает от raw-значений;
- результат хранит raw totals и display totals;
- второй свет / кладка над кухней помечены как case-specific addon.

## Отчёты для руководства

```text
docs/report_pdf_parser.md
docs/report_earthworks_calculator.md
docs/report_foundation_slab_calculator.md
docs/report_floor_slab_1_calculator.md
docs/report_floor_slab_2_calculator.md
docs/report_flat_roof_calculator.md
docs/report_schiedel_vent_channels_calculator.md
docs/report_waterproofing_calculator.md
docs/report_load_bearing_walls_lintels_calculator.md
```

## Handoff для нового чата

Если нужно быстро восстановить контекст, начинать с:

```text
docs/assistant_handoff.md
README.md
docs/current_project_state.md
docs/project_notes.md
```

## Что не забыть

- Не удалять старые файлы из `data/` без отдельной задачи: они могут быть нужны как история.
- При добавлении нового дома сразу создавать проектную папку.
- При добавлении нового расчёта сразу делать `cases/index.md` или обновлять существующий индекс.
- Внутреннюю себестоимость не смешивать с клиентской частью сметы.
- Если итог Excel отличается на округление, не подгонять молча: фиксировать причину в notes/result.
- Перед новым большим этапом проверять, что handoff/current state/changelog отражают последнюю контрольную точку.
