from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import base64
import json
import logging
import mimetypes
import os
import re

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = EXPERIMENT_ROOT / "prompts"

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MEETING_ANALYSIS_MODEL", os.getenv("OPENAI_PROJECT_CARD_MODEL", "gpt-4.1-mini"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LOGGER = logging.getLogger("meeting_analysis_experiment")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
PDF_EXTENSIONS = {".pdf"}
TEXT_EXAMPLE_EXTENSIONS = {".txt", ".md", ".csv"}


@dataclass(frozen=True)
class MeetingInput:
    input_dir: Path
    transcript_files: list[Path]
    combined_text: str
    examples: list[Path]


def collect_meeting_input(raw_input_dir: str) -> MeetingInput:
    input_dir = resolve_input_dir(raw_input_dir)
    transcript_files = sorted(
        [path for path in input_dir.glob("*.txt") if not path.name.startswith(".")],
        key=natural_sort_key,
    )
    if not transcript_files:
        raise FileNotFoundError(f"No .txt transcript files found in: {input_dir}")

    chunks = []
    for path in transcript_files:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            chunks.append(f"=== TRANSCRIPT FILE: {path.name} ===\n\n{text}")

    if not chunks:
        raise ValueError("Transcript files are empty.")

    examples_dir = input_dir / "examples"
    examples = []
    if examples_dir.exists():
        examples = sorted(
            [path for path in examples_dir.rglob("*") if path.is_file() and not is_hidden_path(path, examples_dir)],
            key=lambda item: natural_sort_key(str(item.relative_to(examples_dir))),
        )

    return MeetingInput(
        input_dir=input_dir,
        transcript_files=transcript_files,
        combined_text="\n\n".join(chunks),
        examples=examples,
    )


def resolve_input_dir(raw_input_dir: str) -> Path:
    path = Path(raw_input_dir.strip())
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"Input folder not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Input path is not a folder: {path}")
    return path


def natural_sort_key(value: str | Path) -> list[int | str]:
    text = str(value).lower()
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text)]


def is_hidden_path(path: Path, base_dir: Path) -> bool:
    return any(part.startswith(".") for part in path.relative_to(base_dir).parts)


def analyze_meeting(meeting_input: MeetingInput, mode: str = "with_examples") -> tuple[dict, dict]:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is empty. Add it to your .env file.")

    prompt = build_prompt(mode)
    payload = build_openai_payload(prompt, meeting_input, mode)
    response_json = call_openai(payload)
    analysis = extract_json_from_response(response_json)
    return normalize_analysis(analysis), response_json


def build_prompt(mode: str) -> str:
    prompt_parts = [
        read_prompt("meeting_summary_prompt.txt"),
        read_prompt("calculation_logic_prompt.txt"),
        read_prompt("formulas_prompt.txt"),
        read_prompt("open_questions_prompt.txt"),
        build_output_schema_prompt(mode),
    ]
    return "\n\n".join(part.strip() for part in prompt_parts if part.strip())


def read_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def build_output_schema_prompt(mode: str) -> str:
    examples_instruction = (
        "Режим with_examples включен. Если переданы скрины сметы, PDF-листы проекта или текстовые образцы, "
        "используй их как точечные примеры связки входных данных проекта и результата в смете. "
        "Не анализируй их как полный проект и не обобщай за пределы видимого фрагмента."
        if mode == "with_examples"
        else "Режим без примеров. Используй только транскрипт."
    )

    return f"""
{examples_instruction}

Верни строго валидный JSON-объект с ключами:
- meeting_summary_md: markdown для файла meeting_summary.md
- calculation_logic_md: markdown для файла calculation_logic.md
- formulas_md: markdown для файла formulas.md
- parameters_table: массив объектов для Excel, где каждый объект содержит ключи:
  estimate_section, line_item, required_parameter, source_in_project, formula,
  coefficient, rounding_rule, default_value, manual_review_required, comment
- open_questions_md: markdown для файла open_questions.md
- project_requirements_md: markdown для файла project_requirements.md

Правила:
- Не придумывай формулы, коэффициенты, округления и значения по умолчанию.
- Если формула неполная, явно пиши "требует уточнения".
- Сохраняй короткие цитаты из транскрипта как подтверждение.
- Не делай расчеты стоимости и не подбирай цены.
- Если обсуждались земляные работы, выдели их как отдельный раздел сметы.
- Если пример противоречит транскрипту, ставь вопрос в open_questions_md.
"""


def build_openai_payload(prompt: str, meeting_input: MeetingInput, mode: str) -> dict:
    user_content: list[dict[str, Any]] = [
        {
            "type": "input_text",
            "text": build_user_text(meeting_input, mode),
        }
    ]

    if mode == "with_examples":
        user_content.extend(build_example_content(meeting_input.examples))

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
                            "Не используй markdown вне значений JSON и не добавляй кодовые блоки."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "text": {"format": {"type": "json_object"}},
    }


def build_user_text(meeting_input: MeetingInput, mode: str) -> str:
    examples = describe_examples(meeting_input.examples)
    return f"""
Тема анализа определяется по папке: {meeting_input.input_dir.name}
Режим анализа: {mode}

Задача:
Извлечь из созвона с инженером-сметчиком логику расчётов для MVP AI-сметчика.
Это экспериментальный контур, не production.

Файлы транскрипта прочитаны в порядке имени файла:
{chr(10).join(f"- {path.name}" for path in meeting_input.transcript_files)}

Точечные примеры в папке examples:
{examples}

Объединенный транскрипт:

{meeting_input.combined_text}
""".strip()


def describe_examples(examples: list[Path]) -> str:
    if not examples:
        return "- Нет примеров"

    lines = []
    for path in examples:
        lines.append(f"- {path.name} ({path.suffix.lower() or 'no extension'})")
    return "\n".join(lines)


def build_example_content(examples: list[Path]) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = []
    for path in examples:
        suffix = path.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            content.append({"type": "input_text", "text": f"Точечный визуальный пример: {path.name}"})
            content.append({"type": "input_image", "image_url": encode_file_as_data_url(path)})
        elif suffix in PDF_EXTENSIONS:
            content.append({"type": "input_text", "text": f"Точечный PDF-пример: {path.name}"})
            content.append(
                {
                    "type": "input_file",
                    "filename": path.name,
                    "file_data": encode_file_as_data_url(path),
                }
            )
        elif suffix in TEXT_EXAMPLE_EXTENSIONS:
            content.append(
                {
                    "type": "input_text",
                    "text": f"=== EXAMPLE FILE: {path.name} ===\n\n{path.read_text(encoding='utf-8').strip()}",
                }
            )
        else:
            content.append(
                {
                    "type": "input_text",
                    "text": (
                        f"Файл примера {path.name} найден, но не передан в AI: "
                        "поддерживаются .png/.jpg/.jpeg/.webp/.gif/.pdf/.txt/.md/.csv."
                    ),
                }
            )
    return content


def encode_file_as_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def call_openai(payload: dict) -> dict:
    response = requests.post(
        f"{OPENAI_BASE_URL}/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=300,
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


def normalize_analysis(analysis: dict) -> dict:
    normalized = {
        "meeting_summary_md": str(analysis.get("meeting_summary_md") or "# Summary\n\nНет данных.\n"),
        "calculation_logic_md": str(analysis.get("calculation_logic_md") or "# Calculation Logic\n\nНет данных.\n"),
        "formulas_md": str(analysis.get("formulas_md") or "# Formulas\n\nНет данных.\n"),
        "parameters_table": normalize_parameters_table(analysis.get("parameters_table")),
        "open_questions_md": str(analysis.get("open_questions_md") or "# Open Questions\n\nНет данных.\n"),
        "project_requirements_md": str(analysis.get("project_requirements_md") or "# Project Requirements\n\nНет данных.\n"),
    }
    return normalized


def normalize_parameters_table(value: Any) -> list[dict]:
    columns = parameter_table_columns()
    if not isinstance(value, list):
        return []

    rows = []
    for item in value:
        row = {column: "" for column in columns}
        if isinstance(item, dict):
            for column in columns:
                row[column] = item.get(column, "")
        rows.append(row)
    return rows


def parameter_table_columns() -> list[str]:
    return [
        "estimate_section",
        "line_item",
        "required_parameter",
        "source_in_project",
        "formula",
        "coefficient",
        "rounding_rule",
        "default_value",
        "manual_review_required",
        "comment",
    ]
