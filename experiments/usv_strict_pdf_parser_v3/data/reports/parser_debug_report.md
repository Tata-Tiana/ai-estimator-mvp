# Parser Debug Report

## Песок

- value: 96.6
- fragment: Песок (300 мм) Купл=0,95 96,6 м3
7 7
2 000 8 085 4 4 ГОСТ 5670 4- 2015 П р о ф и л ирова н н ая мембрана 3 2 0 м 2
0 0 6 1 0 0 3 0 0 4 0 0 5 К 1 PL A N T E R К 2 Во д а Эл. кабель И т ого
2
2 000 701 0 0 Длина 51,209 14,5 12,61 20,69
4
ВВВв
- rule: last number before `м3` after keyword `Песок`.

## Траншеи

- routes_count: 4
- total_volume: 32.38
- routes: [{"route_name": "К1", "length_m": 51.209, "depth_m": 0.6, "width_m": 0.4, "volume_m3": 12.2, "evidence_id": "ev_c26948829e16c3a3"}, {"route_name": "К2", "length_m": 14.5, "depth_m": 0.6, "width_m": 0.4, "volume_m3": 3.48, "evidence_id": "ev_c26948829e16c3a3"}, {"route_name": "Вода", "length_m": 12.61, "depth_m": 1.7, "width_m": 0.4, "volume_m3": 8.5, "evidence_id": "ev_c26948829e16c3a3"}, {"route_name": "Эл. кабель", "length_m": 20.69, "depth_m": 1.0, "width_m": 0.4, "volume_m3": 8.2, "evidence_id": "ev_c26948829e16c3a3"}]

## Коммуникации

- pipe_items_count: 5
- communications_length_m: 127.0

## Арматура

- rebar_items_count: 13
- excluded_pipe_like_rows: 18
- low_confidence_count: 0

## Балки

- beam_items_count: 0
- beams_total_length_m: 0
- beams_total_concrete_volume_m3: 0
- beams_total_formwork_area_m2: 0
- parser_failure: Beam table was not recognized as structured B-1/B-2/B-3 rows.
