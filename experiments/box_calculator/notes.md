# Notes

- `box_calculator` не заменяет существующие калькуляторы разделов.
- На текущем этапе реализован только allocator доставки арматуры/металла.
- `rebar_metal_delivery_trucks` в foundation slab считается legacy/manual для старых кейсов.
- Новый статус этого параметра: `AUTO_CALCULATED_BY_BOX`.
- Стоимость доставки металла пока выводится как recommended allocation и не прибавляется к section totals.
- Это сделано, чтобы не задвоить доставку, если legacy totals уже содержат строку доставки.
- В будущей Excel-выгрузке exporter должен вставлять allocated delivery line в нужный раздел и исключать legacy line.
- No Excel cell references.
