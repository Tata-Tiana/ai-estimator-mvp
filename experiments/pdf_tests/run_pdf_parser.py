from __future__ import annotations

from pathlib import Path

from logger import get_logger
from pdf_parser import PDFParser


logger = get_logger()


def main() -> None:
    while True:
        print("\nPDF Parser Experiment")
        print("1 - Извлечь текст через PyMuPDF")
        print("2 - Извлечь блоки с координатами")
        print("3 - Извлечь таблицы через pdfplumber")
        print("4 - Полный прогон PDF")
        print("0 - Выход")

        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("Выход.")
            break

        project_name = input(
            "Введите имя проекта (например horoshevka_14), или Enter для старого data/output:\n"
        ).strip()
        run_name = input(
            "Введите имя части PDF (например kr1_below_floor или kr2_above_floor), или Enter по имени файла:\n"
        ).strip()
        pdf_path = input("Введите путь к PDF:\n").strip()
        try:
            parser = PDFParser(project_name=project_name or None)
            resolved_path = resolve_pdf_path(pdf_path)
            if choice == "1":
                handle_text(parser, resolved_path, run_name or None)
            elif choice == "2":
                handle_blocks(parser, resolved_path, run_name or None)
            elif choice == "3":
                handle_tables(parser, resolved_path, run_name or None)
            elif choice == "4":
                handle_full_run(parser, resolved_path, run_name or None)
            else:
                print("Неизвестная команда. Выберите пункт из меню.")
        except Exception as exc:
            logger.exception("CLI action failed: %s", exc)
            print(f"Ошибка: {exc}")


def resolve_pdf_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / raw_path
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    return path


def handle_text(parser: PDFParser, pdf_path: Path, run_name: str | None = None) -> None:
    text_pages = parser.extract_text_pymupdf(pdf_path)
    result_dir, summary = parser.save_results(
        pdf_path,
        text_pages=text_pages,
        run_name=run_name,
    )
    print(f"Страниц текста: {len(text_pages)}")
    print(f"Символов текста: {summary['text_characters']}")
    print(f"Папка результата: {result_dir}")


def handle_blocks(parser: PDFParser, pdf_path: Path, run_name: str | None = None) -> None:
    blocks = parser.extract_blocks_pymupdf(pdf_path)
    result_dir, summary = parser.save_results(pdf_path, blocks=blocks, run_name=run_name)
    block_count = sum(len(item.get("blocks", [])) for item in blocks)
    print(f"Страниц с блоками: {len(blocks)}")
    print(f"Найдено блоков: {block_count}")
    print(f"Папка результата: {result_dir}")
    print(f"Страниц: {summary['pages']}")


def handle_tables(parser: PDFParser, pdf_path: Path, run_name: str | None = None) -> None:
    tables = parser.extract_tables_pdfplumber(pdf_path)
    result_dir, summary = parser.save_results(pdf_path, tables=tables, run_name=run_name)
    print(f"Найдено таблиц: {summary['tables_found']}")
    print(f"Страницы с таблицами: {summary['pages_with_tables']}")
    print(f"Папка результата: {result_dir}")


def handle_full_run(parser: PDFParser, pdf_path: Path, run_name: str | None = None) -> None:
    text_pages = parser.extract_text_pymupdf(pdf_path)
    blocks = parser.extract_blocks_pymupdf(pdf_path)
    tables = parser.extract_tables_pdfplumber(pdf_path)
    result_dir, summary = parser.save_results(
        pdf_path,
        text_pages=text_pages,
        blocks=blocks,
        tables=tables,
        run_name=run_name,
    )

    print("\nКраткое резюме")
    print(f"Файл: {summary['file_name']}")
    print(f"Страниц: {summary['pages']}")
    print(f"Символов текста: {summary['text_characters']}")
    print(f"Найдено таблиц: {summary['tables_found']}")
    print(f"Страницы с таблицами: {summary['pages_with_tables']}")
    print(f"Папка результата: {result_dir}")


if __name__ == "__main__":
    main()
