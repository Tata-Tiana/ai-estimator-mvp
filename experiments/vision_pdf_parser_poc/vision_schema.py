"""A6.0: prompt + target JSON shape for the vision extraction POC.

Deliberately generic — section names only, no project-specific table
shapes, page numbers, or exact values. The model is not told "find
К1/К2/Вода/Эл.кабель"; it is told the 8 estimate sections and a generic
JSON contract.
"""
from __future__ import annotations

SECTIONS = [
    "земляные работы",
    "фундаментная плита",
    "гидроизоляция",
    "стены и перемычки",
    "плиты перекрытия",
    "плоская кровля",
    "вентканалы Schiedel",
]

PROMPT = """Ты извлекаешь данные из строительной проектной документации.

На изображении одна страница PDF проекта дома.

Нужно найти только явно указанные проектные данные, которые могут понадобиться для сметы коробки дома:
- земляные работы;
- фундаментная плита;
- гидроизоляция;
- стены и перемычки;
- плиты перекрытия;
- плоская кровля;
- вентканалы Schiedel.

Не считай смету.
Не придумывай значения.
Если значения нет на странице — не добавляй его.
Если есть таблица — сохрани структуру таблицы.
Если есть строки/колонки маршрутов, материалов, арматуры, бетона, блоков, кровли — извлеки их как JSON.

Верни только JSON, строго в такой структуре:

{
  "page_number": <int>,
  "page_title": <string or null>,
  "found_sections": [<string>, ...],
  "tables": [
    {
      "section": <string>,
      "table_type": <string>,
      "title": <string>,
      "rows": [<string>, ...],
      "columns": [<string>, ...],
      "items": [<object>, ...],
      "totals": [<object>, ...],
      "raw_text": <string>,
      "confidence": <float 0..1>,
      "notes": [<string>, ...]
    }
  ],
  "materials": [
    {
      "section": <string>,
      "name": <string>,
      "quantity": <number>,
      "unit": <string>,
      "raw_text": <string>,
      "confidence": <float 0..1>
    }
  ],
  "scalar_values": [
    {
      "section": <string>,
      "parameter_hint": <string>,
      "value": <number>,
      "unit": <string>,
      "raw_text": <string>,
      "confidence": <float 0..1>
    }
  ],
  "warnings": [<string>, ...]
}

Если видишь таблицу маршрутов коммуникаций (транше/трубы/сети), где строки —
это параметры (например длина, глубина, ширина, объём), а столбцы — разные
маршруты/сети, сохрани её как отдельный элемент в "tables" с
"table_type": "trench_routes" и такой структурой каждого элемента в "items":

{"name": <string маршрута>, "length_m": <number>, "depth_m": <number>, "width_m": <number>, "volume_m3": <number>}

и, если в таблице есть итоговая колонка/строка, добавь в "totals" один
элемент вида {"total_volume_m3": <number>}.

Если видишь спецификацию труб/фитингов (диаметр, длина куска, количество),
сохрани как отдельный элемент "tables" с "table_type": "pipe_items", каждый
элемент "items" вида:

{"name": <string>, "diameter_mm": <number>, "piece_length_m": <number>, "quantity_pcs": <number>}

Если на странице нет ничего релевантного — верни пустые списки, не выдумывай.
"""


TABLE_TYPES_WITH_SPECIAL_SHAPE = {"trench_routes", "pipe_items"}
