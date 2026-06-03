# Parameter Audit Report

Аудит классифицирует текущие missing/manual параметры. Он не меняет калькуляторы, expected.json или section_schema.py.

## Было
- Всего missing/manual: 287
- manual_required: 69
- missing: 218

| Раздел | Всего | missing | manual_required |
| --- | --- | --- | --- |
| Земляные работы | 13 | 6 | 7 |
| Плоская кровля | 33 | 27 | 6 |
| Плита перекрытия 1-го этажа | 66 | 51 | 15 |
| Плита перекрытия 2-го этажа | 29 | 21 | 8 |
| Фундаментная плита | 41 | 35 | 6 |
| Несущие стены и перемычки | 89 | 68 | 21 |
| Вентиляционные каналы Schiedel | 6 | 3 | 3 |
| Гидроизоляция | 10 | 7 | 3 |

## Рекомендованная классификация
| source_status | count | explanation |
| --- | --- | --- |
| AUTO_PROJECT | 140 | Проектные площади, объемы, длины, веса, количества и спецификации. |
| AUTO_CALCULATED | 81 | Raw/display, totals, закупочные количества и производные значения. |
| DEFAULT_VALUE | 26 | Коэффициенты, упаковки, размеры стандартных материалов, технологические настройки. |
| PRICE_DATABASE | 7 | Цены материалов, работ, техники и доставок из price_registry. |
| MANUAL_REQUIRED | 33 | Реальные решения сметчика по объекту или пока неподтвержденные ручные параметры. |
| REQUIRES_VALIDATION | 0 | Нужна отдельная проверка, правило не уверенное. |

## Что уйдет из ручного ввода
| section | parameter | old_status | new_status | reason |
| --- | --- | --- | --- | --- |
| earthworks | sand truck step m3 | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| earthworks | Площадь одного рулона геотекстиля | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| foundation_slab | Площадь одного рулона мембраны | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| foundation_slab | Количество PLANTERBAND на один рулон мембраны | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| foundation_slab | Рабочая площадь листа фанеры | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| foundation_slab | Арматура 1: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 1: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 1: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 1: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 2: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 2: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 2: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 2: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 3: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 3: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 3: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 3: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 4: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 4: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 4: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Арматура 4: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| foundation_slab | Общий вес металла коробки для доставки | missing | AUTO_CALCULATED | Вычисляемое поле. |
| foundation_slab | Ширина листа фанеры | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| foundation_slab | Высота листа фанеры | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| waterproofing | Расход праймера на 1 м2 | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| waterproofing | Количество слоев битумной мастики | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| waterproofing | Вес одного ведра битумной мастики | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| load_bearing_walls_lintels | Расход клея для блоков на 1 м3 кладки | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| load_bearing_walls_lintels | Вес одного мешка пескобетона | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| load_bearing_walls_lintels | Арматура перемычек 1: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Арматура перемычек 1: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Арматура перемычек 1: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Арматура перемычек 1: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Арматура перемычек 2: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Арматура перемычек 2: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Арматура перемычек 2: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Арматура перемычек 2: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| load_bearing_walls_lintels | Минимальный заказ бетона для перемычек | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| load_bearing_walls_lintels | parapet chasing base length m | missing | AUTO_CALCULATED | Вычисляемое поле. |
| load_bearing_walls_lintels | second light chasing base length m | missing | AUTO_CALCULATED | Вычисляемое поле. |
| load_bearing_walls_lintels | parapet rebar base length m | missing | AUTO_CALCULATED | Вычисляемое поле. |
| load_bearing_walls_lintels | second light rebar base length m | missing | AUTO_CALCULATED | Вычисляемое поле. |
| floor_slab_1 | Объем бетона плиты, расчетное значение без округления | missing | AUTO_CALCULATED | Вычисляемое поле. |
| floor_slab_1 | Объем бетона плиты, отображаемое значение | missing | AUTO_CALCULATED | Вычисляемое поле. |
| floor_slab_1 | Балка Б-1: код позиции | manual_required | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Балка Б-1: наименование позиции | manual_required | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Балка Б-2: код позиции | manual_required | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Балка Б-2: наименование позиции | manual_required | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Балка Б-3: код позиции | manual_required | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Балка Б-3: наименование позиции | manual_required | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Стоимость смены автокрана | manual_required | PRICE_DATABASE | Прайсовая позиция, не проектный параметр. |
| floor_slab_1 | Рабочая площадь листа фанеры | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| floor_slab_1 | Эквивалент листов для свесов и доборов | manual_required | AUTO_CALCULATED | Вычисляемое поле. |
| floor_slab_1 | Стоимость смены бетононасоса | missing | PRICE_DATABASE | Прайсовая позиция, не проектный параметр. |
| floor_slab_1 | Арматура 1: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 1: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 1: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 1: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 2: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 2: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 2: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 2: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 3: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 3: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 3: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 3: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 4: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 4: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 4: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 4: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 5: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 5: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 5: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 5: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 6: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 6: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 6: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Арматура 6: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_1 | Процент логистики и снабжения | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| floor_slab_1 | Процент расходных материалов и амортизации инструмента | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| floor_slab_2 | Рабочая площадь листа фанеры | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| floor_slab_2 | Арматура 1: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 1: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 1: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 1: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 2: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 2: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 2: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 2: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 3: код позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 3: наименование позиции | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 3: класс стали | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Арматура 3: диаметр | missing | AUTO_CALCULATED | Каталожное описание позиции арматуры. |
| floor_slab_2 | Минимальное количество баллонов клей-пены | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| floor_slab_2 | Процент логистики | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| floor_slab_2 | Процент расходных материалов | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| flat_roof | Общая площадь кровли | missing | AUTO_CALCULATED | Вычисляемое поле. |
| flat_roof | Суммарная длина парапетов и примыканий | missing | AUTO_CALCULATED | Вычисляемое поле. |
| flat_roof | Площадь рулона пароизоляционной пленки | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| flat_roof | Площадь рулона геотекстиля для плоской части кровли | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| flat_roof | Площадь рулона геотекстиля для парапетов | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| flat_roof | Ширина рулона ПВХ мембраны | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| flat_roof | Длина рулона ПВХ мембраны | missing | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |
| flat_roof | Ожидаемая сумма материала ПВХ мембраны | missing | AUTO_CALCULATED | Вычисляемое поле. |
| flat_roof | Ставка установки кровельного аэратора | missing | PRICE_DATABASE | Прайсовая позиция, не проектный параметр. |
| flat_roof | Ставка установки парапетной кровельной воронки | missing | PRICE_DATABASE | Прайсовая позиция, не проектный параметр. |
| flat_roof | Ставка пробивки отверстия в стене из газоблока | missing | PRICE_DATABASE | Прайсовая позиция, не проектный параметр. |
| flat_roof | Ставка установки внутренней кровельной воронки | missing | PRICE_DATABASE | Прайсовая позиция, не проектный параметр. |
| flat_roof | Сумма расходных материалов по кровле | missing | AUTO_CALCULATED | Вычисляемое поле. |
| flat_roof | Сумма логистики и снабжения по кровле | missing | AUTO_CALCULATED | Вычисляемое поле. |
| flat_roof | Сумма технического надзора | manual_required | PRICE_DATABASE | Фиксированная сметная ставка, не проектный параметр. |
| flat_roof | Заготовительно-складские расходы | manual_required | AUTO_CALCULATED | Вычисляемое поле. |
| schiedel_vent_channels | schiedel masonry total length m | missing | AUTO_CALCULATED | Вычисляемое поле. |
| schiedel_vent_channels | Процент расходных материалов | manual_required | DEFAULT_VALUE | Системная настройка или каталог материала, не вопрос к проектировщику. |

## Что останется ручным
| section | parameter | why_manual |
| --- | --- | --- |
| earthworks | Ручной объем доработки котлована | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| earthworks | Ручной объем песка | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| earthworks | Ручное количество геотекстиля | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| earthworks | manual refinement depth m | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| earthworks | Количество смен для разбивки осей | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| earthworks | Количество смен экскаватора | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| earthworks | Объем ручной доработки котлована для сметы | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| foundation_slab | Количество смен крана для подачи арматуры | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| foundation_slab | Количество смен бетононасоса | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| foundation_slab | Метод расчета фанеры | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| foundation_slab | Правило выбора высоты торца плиты | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| load_bearing_walls_lintels | Количество смен крана для несущих стен | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| load_bearing_walls_lintels | Количество рейсов доставки бетона | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| load_bearing_walls_lintels | Учитывать парапет в расчете | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| load_bearing_walls_lintels | Учитывать кладку второго света | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| load_bearing_walls_lintels | Кладка второго света: учитывать проектную особенность | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| load_bearing_walls_lintels | Учитывать обкладку вентканалов | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| load_bearing_walls_lintels | Количество смен крана для парапета | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_1 | Сумма предложения поставщика по опалубке | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_1 | Ручное количество машин доставки опалубки | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_1 | Количество смен крана для подачи опалубки и арматуры | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_1 | Количество смен бетононасоса | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_2 | Сумма предложения поставщика по аренде опалубки | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_2 | Количество рейсов доставки/вывоза опалубки | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_2 | Количество смен автокрана | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| floor_slab_2 | Количество смен бетононасоса | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| flat_roof | eps50 supplier required volume m3 | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| flat_roof | slope plate a supplier required volume m3 | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| flat_roof | slope plate b supplier required volume m3 | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| flat_roof | slope plate j supplier required volume m3 | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| flat_roof | slope plate k supplier required volume m3 | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| flat_roof | Количество смен автокрана для подъема кровельных материалов | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |
| schiedel_vent_channels | Количество доставок вентканалов Schiedel | Похоже на решение сметчика, поставщика или case-specific параметр; оставить видимым до подтвержденного правила. |

## Рекомендации по изменению section_schema.py
| calculator_input_key | old_input_type | new_input_type | visible_to_elena | default/formula/source |
| --- | --- | --- | --- | --- |
| assumptions.manual_excavation_override | manual | manual | True | Elena/manual project decision |
| assumptions.sand_override | manual | manual | True | Elena/manual project decision |
| assumptions.geotextile_override | manual | manual | True | Elena/manual project decision |
| pit_area_m2 | parsed | parsed | True | Project PDF/specification/review card |
| manual_refinement_depth_m | manual | manual | True | Elena/manual project decision |
| trench_volume_m3 | parsed | parsed | True | Project PDF/specification/review card |
| sand_truck_step_m3 | parsed | default | False | future defaults_registry.py / material_catalog.py |
| geotextile_roll_area_m2 | parsed | default | False | future defaults_registry.py / material_catalog.py |
| communications_length_m | parsed | parsed | True | Project PDF/specification/review card |
| axis_marking_shifts | manual | manual | True | Elena/manual project decision |
| excavator_shifts | manual | manual | True | Elena/manual project decision |
| geotextile_laying_area_m2 | parsed | parsed | True | Project PDF/specification/review card |
| manual_excavation_quantity_for_estimate_m3 | manual | manual | True | Elena/manual project decision |
| membrane_roll_area_m2 | parsed | default | False | future defaults_registry.py / material_catalog.py |
| planterband_per_membrane_roll | parsed | default | False | future defaults_registry.py / material_catalog.py |
| slab_formwork_perimeter_m | parsed | parsed | True | Project PDF/specification/review card |
| slab_edge_height_m | parsed | parsed | True | Project PDF/specification/review card |
| plywood_sheet_working_area_m2 | parsed | default | False | future defaults_registry.py / material_catalog.py |
| thermal_insert_length_m | parsed | parsed | True | Project PDF/specification/review card |
| thermal_insert_piece_length_m | parsed | parsed | True | Project PDF/specification/review card |
| thermal_insert_piece_width_m | parsed | parsed | True | Project PDF/specification/review card |
| thermal_insert_piece_height_m | parsed | parsed | True | Project PDF/specification/review card |
| thermal_insert_piece_depth_for_work_m | manual | parsed | True | Project PDF/specification/review card |
| thermal_insert_piece_depth_for_eps_m | manual | parsed | True | Project PDF/specification/review card |
| rebar_crane_shifts | manual | manual | True | Elena/manual project decision |
| rebar_items[0].code | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[0].name | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[0].steel_class | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[0].diameter_mm | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[0].weight_parts_kg[0] | parsed | parsed | True | Project PDF/specification/review card |
| rebar_items[1].code | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[1].name | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[1].steel_class | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[1].diameter_mm | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[1].weight_parts_kg[0] | parsed | parsed | True | Project PDF/specification/review card |
| rebar_items[1].weight_parts_kg[1] | parsed | parsed | True | Project PDF/specification/review card |
| rebar_items[2].code | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[2].name | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[2].steel_class | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[2].diameter_mm | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[2].weight_parts_kg[0] | parsed | parsed | True | Project PDF/specification/review card |
| rebar_items[3].code | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[3].name | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[3].steel_class | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[3].diameter_mm | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |
| rebar_items[3].weight_parts_kg[0] | parsed | parsed | True | Project PDF/specification/review card |
| rebar_metal_delivery_trucks | parsed | parsed | True | Project PDF/specification/review card |
| box_total_metal_weight_kg | parsed | calculated | False | total = sum of source line totals / calculated blocks |
| concrete_mixer_volume_m3 | parsed | parsed | True | Project PDF/specification/review card |
| concrete_pump_shifts | manual | manual | True | Elena/manual project decision |
| plywood_calc_method | manual | manual | True | Elena/manual project decision |
| plywood_sheet_width_m | parsed | default | False | future defaults_registry.py / material_catalog.py |
| plywood_sheet_height_m | parsed | default | False | future defaults_registry.py / material_catalog.py |
| slab_edge_height_strategy | manual | manual | True | Elena/manual project decision |
| slab_formwork_perimeter_m | parsed | parsed | True | Project PDF/specification/review card |
| slab_edge_height_m | parsed | parsed | True | Project PDF/specification/review card |
| primer_consumption_l_per_m2 | manual | default | False | future defaults_registry.py / material_catalog.py |
| primer_canister_volume_l | parsed | parsed | True | Project PDF/specification/review card |
| mastic_layers | manual | default | False | future defaults_registry.py / material_catalog.py |
| mastic_bucket_weight_kg | parsed | default | False | future defaults_registry.py / material_catalog.py |
| non_insulated_edge_lengths_m[0] | parsed | parsed | True | Project PDF/specification/review card |
| non_insulated_edge_lengths_m[1] | parsed | parsed | True | Project PDF/specification/review card |
| non_insulated_edge_lengths_m[2] | parsed | parsed | True | Project PDF/specification/review card |
| glue_foam_min_units | manual | parsed | True | Project PDF/specification/review card |
| scaffolding_setup_quantity | manual | parsed | True | Project PDF/specification/review card |
| scaffolding_timber_quantity_m3 | manual | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[0] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[1] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[2] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[3] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[4] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[5] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[6] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[7] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[8] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[9] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[10] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[11] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[12] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[13] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[14] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_400_lengths_m[15] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[0] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[1] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[2] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[3] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[4] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[5] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[6] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[7] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[8] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[9] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[10] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[11] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[12] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[13] | parsed | parsed | True | Project PDF/specification/review card |
| cutoff_waterproofing_wall_250_lengths_m[14] | parsed | parsed | True | Project PDF/specification/review card |
| gas_block_d400_pallet_volume_m3 | parsed | parsed | True | Project PDF/specification/review card |
| gas_block_d500_250_pallet_volume_m3 | parsed | parsed | True | Project PDF/specification/review card |
| adhesive_consumption_bag_per_m3 | manual | default | False | future defaults_registry.py / material_catalog.py |
| sand_concrete_bag_weight_kg | parsed | default | False | future defaults_registry.py / material_catalog.py |
| lintel_lengths_m[0].length_m | parsed | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[0].count | manual | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[1].length_m | parsed | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[1].count | manual | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[2].length_m | parsed | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[2].count | manual | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[3].length_m | parsed | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[3].count | manual | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[4].length_m | parsed | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[4].count | manual | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[5].length_m | parsed | parsed | True | Project PDF/specification/review card |
| lintel_lengths_m[5].count | manual | parsed | True | Project PDF/specification/review card |
| gas_block_length_m | parsed | parsed | True | Project PDF/specification/review card |
| main_wall_external_length_m | parsed | parsed | True | Project PDF/specification/review card |
| main_wall_reinforcement_rows | parsed | parsed | True | Project PDF/specification/review card |
| main_wall_400_reinforcement_threads | parsed | parsed | True | Project PDF/specification/review card |
| main_wall_250_reinforcement_threads | parsed | parsed | True | Project PDF/specification/review card |
| main_walls_crane_shifts | manual | manual | True | Elena/manual project decision |
| lintel_rebar_items[0].code | parsed | calculated | False | Build rebar item metadata from steel class and diameter catalog/specification mapping. |

_Показаны первые 120 строк из 287. Полный список в Excel._

## Ожидаемый эффект
- Было ручных/незаполненных: 287
- Можно убрать из ручного ввода после подтверждения registry/catalog/defaults/derived logic: 114
- Останется реально ручных: 33
- Потенциальное сокращение: 39.7%

## Важные оговорки
- DEFAULT_VALUE не означает автоматическую подстановку старой сметы как универсального норматива.
- Для каждого default нужен источник истины, применимость, возможность override и оценка риска.
- Проектные и case-specific параметры нельзя скрывать без надежного PDF/source или подтвержденной формулы.
- demo_with_template_fallback не является production-расчетом.