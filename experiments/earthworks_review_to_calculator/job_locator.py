from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_JOBS_ROOT = REPO_ROOT / "experiments" / "earthworks_parser_google_stage1" / "data" / "jobs"


def default_jobs_root() -> Path:
    return _DEFAULT_JOBS_ROOT


def resolve_stage1_job_dir(job_id: str, jobs_root: Path | None = None) -> Path:
    root = jobs_root if jobs_root is not None else _DEFAULT_JOBS_ROOT
    job_dir = root / job_id

    if not job_dir.exists():
        raise FileNotFoundError(
            f"Job directory not found: {job_dir}\n"
            f"  job_id: {job_id!r}\n"
            f"  jobs_root: {root}"
        )
    if not job_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {job_dir}")

    metadata_path = job_dir / "google" / "google_sheet_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"google_sheet_metadata.json not found in job directory.\n"
            f"  expected: {metadata_path}\n"
            f"  Is this a valid Stage1 job directory?"
        )

    return job_dir
