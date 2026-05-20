# Project Notes

Дата актуализации: `2026-05-15`.

## Главные договорённости

- AI не считает смету, а помогает достать входные параметры.
- Расчёты делаются детерминированным Python-кодом.
- Любое отличие сметного количества от формульного расчёта фиксируется явно через overrides и notes.
- Для каждого дома должны быть отдельные проектные папки.
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

## Отчёты для руководства

```text
docs/report_pdf_parser.md
docs/report_earthworks_calculator.md
docs/report_foundation_slab_calculator.md
docs/report_waterproofing_calculator.md
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
- Перед новым большим этапом желательно сделать git commit текущей контрольной точки.
