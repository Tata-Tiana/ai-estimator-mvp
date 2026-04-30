from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import json
import logging
import os

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "project_card_prompt.txt"

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

MODEL_NAME = os.getenv("OPENAI_PROJECT_CARD_MODEL", "gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
CHUNK_SIZE = 12000
LOGGER = logging.getLogger("ai_project_card_experiment")


SECTION_FIELDS = {
    "project_summary": [
        "object_name",
        "address",
        "building_type",
        "document_type",
        "short_description",
    ],
    "general_parameters": [
        "house_area",
        "floors",
        "rooms_count",
        "floor_area",
        "premises_area",
        "terrace_area",
        "building_footprint_area",
        "floor_height",
        "total_building_height",
    ],
    "foundation": [
        "foundation_type",
        "slab_thickness",
        "concrete_grade",
        "concrete_volume",
        "reinforcement",
        "reinforcement_quantities",
        "insulation",
        "waterproofing",
        "sand_base",
        "geotextile",
        "piles",
        "embedded_utilities",
    ],
    "walls_and_partitions": [
        "external_wall_material",
        "external_wall_thickness",
        "internal_wall_material",
        "internal_wall_thickness",
        "partition_material",
        "partition_thickness",
        "blocks_specification",
        "wall_reinforcement",
        "lintels",
    ],
    "slabs_and_columns": [
        "floor_slab_type",
        "covering_slab_type",
        "slab_thickness",
        "concrete_grade",
        "concrete_volume",
        "reinforcement",
        "columns",
    ],
    "roof": [
        "roof_type",
        "roof_area",
        "roof_slope",
        "roof_layers",
        "insulation",
        "membrane",
        "drainage",
        "parapet",
        "roof_materials_specification",
    ],
    "ventilation_and_chimneys": [
        "vent_blocks",
        "chimney",
        "quantities",
    ],
    "terrace_and_canopy": [
        "terrace_area",
        "canopy_structure",
        "timber_specification",
        "piles",
    ],
}

FIELD_UNITS = {
    "house_area": "м2",
    "floor_area": "м2",
    "premises_area": "м2",
    "terrace_area": "м2",
    "building_footprint_area": "м2",
    "floor_height": "м",
    "total_building_height": "м",
    "rooms_count": "шт",
    "slab_thickness": "мм",
    "concrete_volume": "м3",
    "external_wall_thickness": "мм",
    "internal_wall_thickness": "мм",
    "partition_thickness": "мм",
    "roof_area": "м2",
}

ESTIMATE_SECTIONS = [
    "подготовительные работы",
    "земляные работы",
    "ростверковый фундамент",
    "плита основания пола",
    "гидроизоляция и утепление стен ростверка и плиты",
    "колонны",
    "внешние стены и перемычки",
    "плиты перекрытия",
    "кровельное покрытие",
    "вентиляционные каналы и дымоход",
    "перегородки",
]


def generate_project_card(text: str) -> dict:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is empty. Add it to your .env file.")

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    chunks = split_text_into_chunks(text, CHUNK_SIZE)

    if len(chunks) == 1:
        return analyze_single_chunk(chunks[0], prompt)

    partial_cards = []
    for index, chunk in enumerate(chunks, start=1):
        partial_prompt = (
            f"{prompt}\n\n"
            "Это только часть документа. Извлекай факты только из этого фрагмента. "
            "Если источник страницы не виден, ставь source_page: null.\n\n"
            f"Номер чанка: {index}/{len(chunks)}"
        )
        partial_cards.append(analyze_single_chunk(chunk, partial_prompt))

    return merge_partial_cards(partial_cards, prompt)


def analyze_single_chunk(text_chunk: str, prompt: str) -> dict:
    payload = build_openai_payload(prompt, text_chunk)
    response_json = call_openai(payload)
    return extract_json_from_response(response_json)


def merge_partial_cards(partial_cards: list[dict], prompt: str) -> dict:
    merge_prompt = (
        f"{prompt}\n\n"
        "Ниже переданы частичные JSON-карточки, собранные по разным чанкам одного или нескольких PDF. "
        "Объедини их в одну итоговую техническую карточку проекта. "
        "Сохрани все инженерные данные. Не придумывай новые факты. "
        "Если есть конфликт, выбери более точное значение и добавь пояснение в warnings или comment. "
        "Не теряй materials_extracted и estimate_scope_mapping."
    )
    partial_json = json.dumps(partial_cards, ensure_ascii=False, indent=2)
    payload = build_openai_payload(merge_prompt, partial_json)
    response_json = call_openai(payload)
    return extract_json_from_response(response_json)


def build_openai_payload(prompt: str, content: str) -> dict:
    return {
        "model": MODEL_NAME,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"{prompt}\n\n"
                            "Ответ должен быть строго валидным JSON-объектом. "
                            "Не используй markdown, пояснения вне JSON или кодовые блоки."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": content}],
            },
        ],
        "text": {"format": {"type": "json_object"}},
    }


def call_openai(payload: dict) -> dict:
    response = requests.post(
        f"{OPENAI_BASE_URL}/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=180,
    )
    if not response.ok:
        error_body = response.text
        if LOGGER.handlers:
            LOGGER.error("OpenAI API error body: %s", error_body)
        raise requests.HTTPError(
            f"{response.status_code} Client Error for url: {response.url}. Response body: {error_body}",
            response=response,
        )
    return response.json()


def extract_json_from_response(response_json: dict) -> dict:
    text_value = response_json.get("output_text")
    if text_value:
        return json.loads(clean_json_text(text_value))

    for item in response_json.get("output", []):
        for content_item in item.get("content", []):
            if content_item.get("type") == "output_text":
                return json.loads(clean_json_text(content_item.get("text", "")))

    raise ValueError("Could not extract JSON from OpenAI response.")


def clean_json_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


def split_text_into_chunks(text: str, max_chars: int) -> list[str]:
    normalized = text.strip()
    if len(normalized) <= max_chars:
        return [normalized]

    paragraphs = normalized.split("\n\n")
    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        candidate = paragraph if not current_chunk else f"{current_chunk}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current_chunk = candidate
            continue

        if current_chunk:
            chunks.append(current_chunk)
        if len(paragraph) <= max_chars:
            current_chunk = paragraph
            continue

        sentence_chunks = hard_split(paragraph, max_chars)
        chunks.extend(sentence_chunks[:-1])
        current_chunk = sentence_chunks[-1]

    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def hard_split(text: str, max_chars: int) -> list[str]:
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = start + max_chars
        parts.append(text[start:end])
        start = end
    return parts


def empty_parameter(unit: str | None = None) -> dict:
    return {
        "value": None,
        "unit": unit,
        "confidence": 0,
        "source_text": None,
        "source_page": None,
        "comment": None,
    }


def empty_material() -> dict:
    return {
        "name": "",
        "normalized_name": "",
        "category": "",
        "quantity": None,
        "unit": None,
        "source_section": "",
        "source_text": "",
        "confidence": 0,
        "needs_manual_review": True,
    }


def empty_estimate_mapping(section_name: str) -> dict:
    return {
        "estimate_section": section_name,
        "found_in_project": False,
        "relevant_project_data": [],
        "missing_for_calculation": [],
        "comment": "",
    }


def empty_project_card() -> dict:
    card = {
        "project_summary": {},
        "general_parameters": {},
        "foundation": {},
        "walls_and_partitions": {},
        "slabs_and_columns": {},
        "roof": {},
        "ventilation_and_chimneys": {},
        "terrace_and_canopy": {},
        "materials_extracted": [],
        "estimate_scope_mapping": [empty_estimate_mapping(item) for item in ESTIMATE_SECTIONS],
        "missing_data": [],
        "warnings": [],
        "human_review_required": [],
    }

    for section_name, fields in SECTION_FIELDS.items():
        section = {}
        for field_name in fields:
            section[field_name] = empty_parameter(FIELD_UNITS.get(field_name))
        card[section_name] = section

    return card


def normalize_project_card(card: dict) -> dict:
    normalized = empty_project_card()
    merged = deep_merge(normalized, card)
    merged = normalize_parameters(merged)
    merged["materials_extracted"] = normalize_materials(merged.get("materials_extracted", []))
    merged["estimate_scope_mapping"] = normalize_estimate_scope_mapping(
        merged.get("estimate_scope_mapping", [])
    )
    merged["missing_data"] = normalize_string_list(merged.get("missing_data", []))
    merged["warnings"] = normalize_string_list(merged.get("warnings", []))
    merged["human_review_required"] = normalize_string_list(merged.get("human_review_required", []))
    return merged


def normalize_parameters(card: dict) -> dict:
    for section_name, fields in SECTION_FIELDS.items():
        section = card.get(section_name, {})
        if not isinstance(section, dict):
            section = {}
            card[section_name] = section
        for field_name in fields:
            section[field_name] = normalize_parameter(section.get(field_name), FIELD_UNITS.get(field_name))
    return card


def normalize_parameter(value: Any, default_unit: str | None) -> dict:
    template = empty_parameter(default_unit)
    if isinstance(value, dict):
        for key in template:
            if key in value:
                template[key] = value[key]
        if template["unit"] is None and default_unit is not None:
            template["unit"] = default_unit
        return template

    if value is None:
        return template

    template["value"] = value
    return template


def normalize_materials(materials: Any) -> list[dict]:
    if not isinstance(materials, list):
        return []

    normalized: list[dict] = []
    for item in materials:
        template = empty_material()
        if isinstance(item, dict):
            for key in template:
                if key in item:
                    template[key] = item[key]
        normalized.append(template)
    return normalized


def normalize_estimate_scope_mapping(items: Any) -> list[dict]:
    if not isinstance(items, list):
        items = []

    indexed = {}
    for item in items:
        if isinstance(item, dict) and item.get("estimate_section"):
            indexed[item["estimate_section"]] = item

    normalized: list[dict] = []
    for section_name in ESTIMATE_SECTIONS:
        template = empty_estimate_mapping(section_name)
        source = indexed.get(section_name, {})
        if isinstance(source, dict):
            for key in template:
                if key in source:
                    template[key] = source[key]
        template["relevant_project_data"] = normalize_string_list(template.get("relevant_project_data", []))
        template["missing_for_calculation"] = normalize_string_list(template.get("missing_for_calculation", []))
        normalized.append(template)
    return normalized


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def deep_merge(base: Any, update: Any) -> Any:
    if isinstance(base, dict) and isinstance(update, dict):
        result = deepcopy(base)
        for key, value in update.items():
            if key in result:
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    if isinstance(base, list) and isinstance(update, list):
        return update

    return update if update is not None else base


def render_project_card_markdown(card: dict) -> str:
    lines = [
        "# Техническая карточка проекта",
        "",
        "## 1. Сводка проекта",
    ]
    lines.extend(render_parameter_section(card.get("project_summary", {}), SECTION_FIELDS["project_summary"]))
    lines.extend(["", "## 2. Общие параметры"])
    lines.extend(render_parameter_section(card.get("general_parameters", {}), SECTION_FIELDS["general_parameters"]))
    lines.extend(["", "## 3. Фундамент"])
    lines.extend(render_parameter_section(card.get("foundation", {}), SECTION_FIELDS["foundation"]))
    lines.extend(["", "## 4. Стены и перегородки"])
    lines.extend(render_parameter_section(card.get("walls_and_partitions", {}), SECTION_FIELDS["walls_and_partitions"]))
    lines.extend(["", "## 5. Перекрытия и колонны"])
    lines.extend(render_parameter_section(card.get("slabs_and_columns", {}), SECTION_FIELDS["slabs_and_columns"]))
    lines.extend(["", "## 6. Кровля"])
    lines.extend(render_parameter_section(card.get("roof", {}), SECTION_FIELDS["roof"]))
    lines.extend(["", "## 7. Вентканалы и дымоход"])
    lines.extend(render_parameter_section(card.get("ventilation_and_chimneys", {}), SECTION_FIELDS["ventilation_and_chimneys"]))
    lines.extend(["", "## 8. Терраса и навес"])
    lines.extend(render_parameter_section(card.get("terrace_and_canopy", {}), SECTION_FIELDS["terrace_and_canopy"]))
    lines.extend(["", "## 9. Извлечённые материалы"])
    lines.extend(render_materials_markdown(card.get("materials_extracted", [])))
    lines.extend(["", "## 10. Сопоставление с разделами сметы"])
    lines.extend(render_estimate_scope_markdown(card.get("estimate_scope_mapping", [])))
    lines.extend(["", "## 11. Недостающие данные"])
    lines.extend(render_string_list(card.get("missing_data", [])))
    lines.extend(["", "## 12. Предупреждения"])
    lines.extend(render_string_list(card.get("warnings", [])))
    lines.extend(["", "## 13. Что должен проверить сметчик"])
    lines.extend(render_string_list(card.get("human_review_required", [])))
    return "\n".join(lines) + "\n"


def render_parameter_section(section: dict, field_names: list[str]) -> list[str]:
    lines: list[str] = []
    for field_name in field_names:
        lines.append(f"- {humanize_field_name(field_name)}: {format_parameter(section.get(field_name))}")
    return lines


def render_materials_markdown(materials: list[dict]) -> list[str]:
    if not materials:
        return ["- Нет данных"]
    lines = []
    for item in materials:
        lines.append(
            "- "
            f"{item.get('name') or 'Без названия'} | "
            f"normalized: {item.get('normalized_name') or '-'} | "
            f"category: {item.get('category') or '-'} | "
            f"qty: {item.get('quantity')} {item.get('unit') or ''} | "
            f"manual_review: {item.get('needs_manual_review')}"
        )
    return lines


def render_estimate_scope_markdown(items: list[dict]) -> list[str]:
    if not items:
        return ["- Нет данных"]
    lines = []
    for item in items:
        lines.append(
            f"- {item.get('estimate_section')}: "
            f"found={item.get('found_in_project')}, "
            f"missing={'; '.join(item.get('missing_for_calculation', [])) or '-'}, "
            f"comment={item.get('comment') or '-'}"
        )
    return lines


def render_string_list(items: list[str]) -> list[str]:
    if not items:
        return ["- Нет"]
    return [f"- {item}" for item in items]


def format_parameter(parameter: Any) -> str:
    if isinstance(parameter, dict) and {"value", "unit", "confidence", "source_text", "source_page", "comment"}.issubset(parameter.keys()):
        value = parameter.get("value")
        unit = parameter.get("unit")
        confidence = parameter.get("confidence", 0)
        source_text = parameter.get("source_text")
        source_page = parameter.get("source_page")
        comment = parameter.get("comment")

        parts = ["null" if value is None else str(value)]
        if unit:
            parts.append(unit)
        parts.append(f"(confidence: {confidence})")
        if source_page is not None:
            parts.append(f"[page: {source_page}]")
        if source_text:
            parts.append(f'quote: "{source_text}"')
        if comment:
            parts.append(f"- {comment}")
        return " ".join(parts)

    if parameter is None:
        return "null"
    return str(parameter)


def humanize_field_name(name: str) -> str:
    return name.replace("_", " ")
