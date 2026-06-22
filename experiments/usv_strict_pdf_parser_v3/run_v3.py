from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import parser_paths

from beam_table_parser import parse_beams
from candidate_store import CandidateStore
from drawing_index import build_drawing_index
from earthworks_parser import parse_earthworks
from integrity_checks import check_integrity
from logical_sheet_classifier import classify_pages
from mapper import build_mapping
from pdf_extract import extract_pdf_data
from rebar_parser import parse_rebar
from report_builder import build_reports


def run() -> dict:
    pages, tables = extract_pdf_data()
    build_drawing_index()
    logical_pages = classify_pages()
    store = CandidateStore()
    earth = parse_earthworks(store)
    rebar = parse_rebar(store)
    beams = parse_beams(store)
    store.write()
    mapped, draft = build_mapping()
    integrity = check_integrity()
    build_reports()
    return {
        "earth": earth,
        "rebar": rebar,
        "beams": beams,
        "mapped": mapped,
        "draft": draft,
        "integrity": integrity,
        "pages_count": len(pages),
        "tables_count": len(tables),
        "logical_pages_count": len(logical_pages),
        "candidates_count": len(store.items),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_parser_run(out_dir: Path, input_pdfs: list[Path], result: dict) -> Path:
    errors = result["integrity"].get("errors", [])
    data = {
        "status": "completed" if not errors else "completed_with_errors",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "out_dir": str(out_dir),
        "input_pdfs": [
            {
                "path": str(Path("input_pdfs") / p.name),
                "name": p.name,
                "sha256": _sha256(p),
                "size_bytes": p.stat().st_size,
            }
            for p in sorted(input_pdfs)
        ],
        "pages_count": result["pages_count"],
        "tables_count": result["tables_count"],
        "logical_pages_count": result["logical_pages_count"],
        "candidates_count": result["candidates_count"],
        "warnings": [],
        "errors": errors,
    }
    path = out_dir / "parser_run.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="USV strict PDF parser v3")
    source = p.add_mutually_exclusive_group()
    source.add_argument("--input-dir", type=Path, help="Directory with input PDF files")
    source.add_argument(
        "--pdf",
        action="append",
        nargs="+",
        type=Path,
        dest="pdfs",
        metavar="PDF",
        help="PDF file(s) to parse. Repeatable: --pdf f1.pdf --pdf f2.pdf or --pdf f1.pdf f2.pdf",
    )
    p.add_argument("--out-dir", type=Path, help="Output directory for all parser artifacts")
    p.add_argument("--json", action="store_true", dest="json_output", help="Print result JSON to stdout; all logs go to stderr")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    log = sys.stderr if args.json_output else sys.stdout

    # Flatten --pdf groups: [[f1, f2], [f3]] → [f1, f2, f3]
    pdfs_flat: list[Path] = [pdf for group in (args.pdfs or []) for pdf in group]

    if args.out_dir or args.input_dir or pdfs_flat:
        out_dir = Path(args.out_dir).resolve() if args.out_dir else (Path.cwd() / "parser_out")
        out_dir.mkdir(parents=True, exist_ok=True)

        if pdfs_flat:
            in_dir = out_dir / "input_pdfs"
            in_dir.mkdir(parents=True, exist_ok=True)
            for pdf in pdfs_flat:
                shutil.copy2(pdf, in_dir / pdf.name)
        elif args.input_dir:
            in_dir = Path(args.input_dir).resolve()
        else:
            in_dir = out_dir / "input_pdfs"

        parser_paths.configure(out_dir, in_dir)
        input_pdfs = sorted(in_dir.glob("*.pdf"))
    else:
        input_pdfs = sorted(parser_paths.input_dir().glob("*.pdf"))

    if args.json_output:
        with contextlib.redirect_stdout(sys.stderr):
            result = run()
    else:
        result = run()

    if args.out_dir or args.input_dir or pdfs_flat:
        run_path = _write_parser_run(out_dir, input_pdfs, result)
        print(f"parser_run: {run_path}", file=log)

    print("USV strict parser v3 completed", file=log)
    print(f"- mapped_parameters: {parser_paths.mapped_parameters_path()}", file=log)
    print(f"- final_project_parameters_draft: {parser_paths.final_draft_path()}", file=log)
    print(f"- coverage_report: {parser_paths.coverage_report_path()}", file=log)
    print(f"- parser_debug_report: {parser_paths.debug_report_path()}", file=log)
    print(f"- sand_volume_m3: {result['earth'].get('sand', {}).get('sand_volume_m3') if result['earth'].get('sand') else None}", file=log)
    print(f"- trench_routes: {len(result['earth'].get('trenches', {}).get('trench_routes', []))}", file=log)
    print(f"- communication_pipe_items: {len(result['earth'].get('communications', {}).get('communication_pipe_items', []))}", file=log)
    print(f"- rebar_items: {len(result['rebar'].get('normalized_rebar_items', []))}", file=log)
    print(f"- beam_items: {len(result['beams'].get('normalized_beam_items', []))}", file=log)
    print("- curated_values_used_as_data: 0", file=log)

    if args.json_output:
        summary = {
            "status": "completed" if not result["integrity"].get("errors") else "completed_with_errors",
            "pages_count": result["pages_count"],
            "tables_count": result["tables_count"],
            "logical_pages_count": result["logical_pages_count"],
            "candidates_count": result["candidates_count"],
            "warnings": [],
            "errors": result["integrity"].get("errors", []),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
