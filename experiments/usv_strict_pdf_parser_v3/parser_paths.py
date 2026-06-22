from __future__ import annotations

from pathlib import Path


_BASE_DIR = Path(__file__).resolve().parent
_DEFAULT_DATA_DIR = _BASE_DIR / "data"

_out_dir: Path | None = None
_in_dir: Path | None = None


def configure(out_dir: Path, in_dir: Path) -> None:
    global _out_dir, _in_dir
    _out_dir = Path(out_dir).resolve()
    _in_dir = Path(in_dir).resolve()


def _data_dir() -> Path:
    return _out_dir if _out_dir is not None else _DEFAULT_DATA_DIR


def input_dir() -> Path:
    return _in_dir if _in_dir is not None else (_DEFAULT_DATA_DIR / "input_pdfs")


def raw_dir() -> Path:
    return _data_dir() / "raw"


def extracted_dir() -> Path:
    return _data_dir() / "extracted"


def mapped_dir() -> Path:
    return _data_dir() / "mapped"


def reports_dir() -> Path:
    return _data_dir() / "reports"


def pages_text_path() -> Path:
    return raw_dir() / "pages_text.json"


def tables_path() -> Path:
    return raw_dir() / "tables.json"


def drawing_index_path() -> Path:
    return raw_dir() / "drawing_index.json"


def logical_pages_path() -> Path:
    return raw_dir() / "logical_pages.json"


def candidates_path() -> Path:
    return extracted_dir() / "candidates.json"


def earthworks_path() -> Path:
    return extracted_dir() / "earthworks.json"


def rebar_items_path() -> Path:
    return extracted_dir() / "rebar_items.json"


def beam_items_path() -> Path:
    return extracted_dir() / "beam_items.json"


def final_draft_path() -> Path:
    return mapped_dir() / "final_project_parameters_draft.json"


def mapped_parameters_path() -> Path:
    return mapped_dir() / "mapped_parameters.json"


def coverage_report_path() -> Path:
    return reports_dir() / "coverage_report.md"


def debug_report_path() -> Path:
    return reports_dir() / "parser_debug_report.md"


def integrity_report_path() -> Path:
    return reports_dir() / "integrity_report.md"
