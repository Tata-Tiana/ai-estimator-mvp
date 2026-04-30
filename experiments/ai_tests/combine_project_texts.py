from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import logging


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "data" / "output" / "pdf_experiments"
LOG_DIR = PROJECT_ROOT / "data" / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
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

    raw_path_1 = input("Введите путь к первому full_text.txt:\n").strip()
    raw_path_2 = input("Введите путь ко второму full_text.txt:\n").strip()

    try:
        path_1 = resolve_input_path(raw_path_1)
        path_2 = resolve_input_path(raw_path_2)
        result_dir = combine_texts(path_1, path_2)
        logger.info("Combined text saved to: %s", result_dir)
        print(f"Готово. Общий текст сохранен в: {result_dir}")
    except Exception as exc:
        logger.exception("Combining project texts failed: %s", exc)
        print(f"Ошибка: {exc}")


def resolve_input_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / raw_path
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path


def combine_texts(path_1: Path, path_2: Path) -> Path:
    text_1 = path_1.read_text(encoding="utf-8")
    text_2 = path_2.read_text(encoding="utf-8")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    result_dir = OUTPUT_ROOT / f"combined_project_{timestamp}"
    result_dir.mkdir(parents=True, exist_ok=True)

    combined_text = (
        "=== DOCUMENT 1 START ===\n"
        f"Source: {path_1}\n\n"
        f"{text_1.strip()}\n\n"
        "=== DOCUMENT 1 END ===\n\n"
        "=== DOCUMENT 2 START ===\n"
        f"Source: {path_2}\n\n"
        f"{text_2.strip()}\n\n"
        "=== DOCUMENT 2 END ===\n"
    )

    combined_path = result_dir / "full_text.txt"
    sources_path = result_dir / "sources.json"
    summary_path = result_dir / "summary.json"

    combined_path.write_text(combined_text, encoding="utf-8")
    sources_path.write_text(
        json.dumps(
            {
                "sources": [str(path_1), str(path_2)],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(
            {
                "result_dir": str(result_dir),
                "combined_file": str(combined_path),
                "source_files": [str(path_1), str(path_2)],
                "source_sizes": [len(text_1), len(text_2)],
                "combined_size": len(combined_text),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    logger = get_logger()
    logger.info("Combined sources: %s | %s", path_1, path_2)
    logger.info("Combined text size: %s characters", len(combined_text))
    return result_dir


if __name__ == "__main__":
    main()
