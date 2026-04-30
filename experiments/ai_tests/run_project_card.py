from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import logging

import pandas as pd

from project_card_ai import MODEL_NAME, generate_project_card, normalize_project_card, render_project_card_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "data" / "output" / "logs"
OUTPUT_ROOT = PROJECT_ROOT / "data" / "output" / "ai_project_cards"
LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "ai_project_card_experiment.log"


def get_logger() -> logging.Logger:
    logger = logging.getLogger("ai_project_card_experiment")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def main() -> None:
    logger = get_logger()

    print("1 - Сформировать карточку из одного full_text.txt")
    print("2 - Сформировать карточку из нескольких full_text.txt")
    choice = input("Выберите действие:\n").strip()

    try:
        input_files = collect_input_files(choice)
        combined_text = build_combined_text(input_files)
        output_dir = OUTPUT_ROOT / datetime.now().strftime("%Y-%m-%d_%H%M")
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Input files count: %s", len(input_files))
        logger.info("Input files: %s", ", ".join(str(item) for item in input_files))
        logger.info("Total text size: %s characters", len(combined_text))
        logger.info("Model: %s", MODEL_NAME)

        save_input_bundle(output_dir, input_files, combined_text)
        project_card = normalize_project_card(generate_project_card(combined_text))
        save_results(output_dir, project_card, input_files, combined_text)

        logger.info("Result saved to: %s", output_dir)
        print(f"Готово. Результат сохранен в: {output_dir}")
    except Exception as exc:
        logger.exception("Project card generation failed: %s", exc)
        print(f"Ошибка: {exc}")


def collect_input_files(choice: str) -> list[Path]:
    if choice == "1":
        raw_path = input("Введите путь к full_text.txt:\n").strip()
        return [resolve_input_path(raw_path)]

    if choice == "2":
        raw_paths = input("Введите пути к full_text.txt через запятую:\n").strip()
        parts = [item.strip() for item in raw_paths.split(",") if item.strip()]
        if not parts:
            raise ValueError("No input files provided.")
        return [resolve_input_path(item) for item in parts]

    raise ValueError("Unknown menu option.")


def resolve_input_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / raw_path
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path


def build_combined_text(input_files: list[Path]) -> str:
    chunks = []
    for path in input_files:
        text = path.read_text(encoding="utf-8")
        chunks.append(f"=== SOURCE FILE: {path.name} ===\n\n{text.strip()}")
    return "\n\n".join(chunks)


def save_results(output_dir: Path, project_card: dict, input_files: list[Path], combined_text: str) -> None:
    (output_dir / "project_card_full.json").write_text(
        json.dumps(project_card, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "project_card_full.md").write_text(
        render_project_card_markdown(project_card),
        encoding="utf-8",
    )
    (output_dir / "missing_data.txt").write_text(
        "\n".join(project_card.get("missing_data", [])) + ("\n" if project_card.get("missing_data") else ""),
        encoding="utf-8",
    )
    (output_dir / "warnings.txt").write_text(
        "\n".join(project_card.get("warnings", [])) + ("\n" if project_card.get("warnings") else ""),
        encoding="utf-8",
    )
    save_materials_excel(output_dir / "materials_extracted.xlsx", project_card.get("materials_extracted", []))
    save_estimate_scope_excel(output_dir / "estimate_scope_mapping.xlsx", project_card.get("estimate_scope_mapping", []))


def save_input_bundle(output_dir: Path, input_files: list[Path], combined_text: str) -> None:
    (output_dir / "full_text_combined.txt").write_text(combined_text, encoding="utf-8")
    (output_dir / "sources.json").write_text(
        json.dumps(
            {
                "input_files": [str(path) for path in input_files],
                "combined_text_file": str(output_dir / "full_text_combined.txt"),
                "combined_text_size": len(combined_text),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def save_materials_excel(path: Path, materials: list[dict]) -> None:
    rows = []
    for item in materials:
        rows.append(
            {
                "name": item.get("name"),
                "normalized_name": item.get("normalized_name"),
                "category": item.get("category"),
                "quantity": item.get("quantity"),
                "unit": item.get("unit"),
                "source_section": item.get("source_section"),
                "source_text": item.get("source_text"),
                "confidence": item.get("confidence"),
                "needs_manual_review": item.get("needs_manual_review"),
            }
        )

    dataframe = pd.DataFrame(rows, columns=[
        "name",
        "normalized_name",
        "category",
        "quantity",
        "unit",
        "source_section",
        "source_text",
        "confidence",
        "needs_manual_review",
    ])
    if dataframe.empty:
        dataframe = pd.DataFrame(columns=dataframe.columns)
    dataframe.to_excel(path, index=False)


def save_estimate_scope_excel(path: Path, items: list[dict]) -> None:
    rows = []
    for item in items:
        rows.append(
            {
                "estimate_section": item.get("estimate_section"),
                "found_in_project": item.get("found_in_project"),
                "relevant_project_data": "; ".join(item.get("relevant_project_data", [])),
                "missing_for_calculation": "; ".join(item.get("missing_for_calculation", [])),
                "comment": item.get("comment"),
            }
        )

    dataframe = pd.DataFrame(rows, columns=[
        "estimate_section",
        "found_in_project",
        "relevant_project_data",
        "missing_for_calculation",
        "comment",
    ])
    if dataframe.empty:
        dataframe = pd.DataFrame(columns=dataframe.columns)
    dataframe.to_excel(path, index=False)


if __name__ == "__main__":
    main()
