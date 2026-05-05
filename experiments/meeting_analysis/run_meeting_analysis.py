from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re

import pandas as pd

from logger import get_logger
from meeting_analyzer import (
    MODEL_NAME,
    PROJECT_ROOT,
    analyze_meeting,
    collect_meeting_input,
    parameter_table_columns,
)


OUTPUT_ROOT = PROJECT_ROOT / "data" / "output" / "meeting_analysis"


def main() -> None:
    logger = get_logger()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    print("Анализ транскриптов созвона с инженером-сметчиком")
    print("Пример папки: experiments/meeting_analysis/input/2026-04-30_earthworks/")
    raw_input_dir = input("Введите путь к папке с транскриптами:\n").strip()

    mode_choice = input("Использовать точечные примеры из подпапки examples? [Y/n]\n").strip().lower()
    mode = "without_examples" if mode_choice in {"n", "no", "нет"} else "with_examples"

    try:
        meeting_input = collect_meeting_input(raw_input_dir)
        topic = extract_topic(meeting_input.input_dir.name)
        output_dir = OUTPUT_ROOT / f"{datetime.now().strftime('%Y-%m-%d_%H%M')}_{topic}"
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Input folder: %s", meeting_input.input_dir)
        logger.info("Transcript files count: %s", len(meeting_input.transcript_files))
        logger.info("Examples count: %s", len(meeting_input.examples))
        logger.info("Mode: %s", mode)
        logger.info("Model: %s", MODEL_NAME)

        save_sources(output_dir, meeting_input, mode)
        analysis, raw_response = analyze_meeting(meeting_input, mode=mode)
        save_results(output_dir, analysis, raw_response)

        logger.info("Result saved to: %s", output_dir)
        print(f"Готово. Результат сохранен в: {output_dir}")
    except Exception as exc:
        logger.exception("Meeting analysis failed: %s", exc)
        print(f"Ошибка: {exc}")


def extract_topic(folder_name: str) -> str:
    topic = re.sub(r"^\d{4}-\d{2}-\d{2}[_-]?", "", folder_name.strip())
    topic = topic or folder_name
    topic = re.sub(r"[^A-Za-zА-Яа-я0-9_-]+", "_", topic)
    return topic.strip("_") or "meeting"


def save_sources(output_dir: Path, meeting_input, mode: str) -> None:
    (output_dir / "combined_transcript.txt").write_text(meeting_input.combined_text, encoding="utf-8")
    (output_dir / "sources.json").write_text(
        json.dumps(
            {
                "input_dir": str(meeting_input.input_dir),
                "mode": mode,
                "model": MODEL_NAME,
                "transcript_files": [str(path) for path in meeting_input.transcript_files],
                "examples": [str(path) for path in meeting_input.examples],
                "combined_transcript_file": str(output_dir / "combined_transcript.txt"),
                "combined_transcript_size": len(meeting_input.combined_text),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def save_results(output_dir: Path, analysis: dict, raw_response: dict) -> None:
    (output_dir / "meeting_summary.md").write_text(ensure_trailing_newline(analysis["meeting_summary_md"]), encoding="utf-8")
    (output_dir / "calculation_logic.md").write_text(ensure_trailing_newline(analysis["calculation_logic_md"]), encoding="utf-8")
    (output_dir / "formulas.md").write_text(ensure_trailing_newline(analysis["formulas_md"]), encoding="utf-8")
    (output_dir / "open_questions.md").write_text(ensure_trailing_newline(analysis["open_questions_md"]), encoding="utf-8")
    (output_dir / "project_requirements.md").write_text(
        ensure_trailing_newline(analysis["project_requirements_md"]),
        encoding="utf-8",
    )
    (output_dir / "raw_ai_response.json").write_text(
        json.dumps(raw_response, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    dataframe = pd.DataFrame(analysis["parameters_table"], columns=parameter_table_columns())
    if dataframe.empty:
        dataframe = pd.DataFrame(columns=parameter_table_columns())
    dataframe.to_excel(output_dir / "parameters_table.xlsx", index=False)


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else f"{text}\n"


if __name__ == "__main__":
    main()
