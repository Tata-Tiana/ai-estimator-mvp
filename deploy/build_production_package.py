from __future__ import annotations

import argparse
import hashlib
import tarfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = Path(__file__).with_name("production_manifest.txt")
ARCHIVE_ROOT = "ai-estimator-mvp"
FORBIDDEN_PARTS = {".env", "__pycache__", ".pytest_cache", ".DS_Store"}
FORBIDDEN_NAME_PARTS = ("token", "credentials", "client_secret", "service_account")


def _manifest_patterns(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _is_allowed(path: Path) -> bool:
    relative = path.relative_to(REPO_ROOT)
    if any(part in FORBIDDEN_PARTS for part in relative.parts):
        return False
    lowered = path.name.lower()
    if any(fragment in lowered for fragment in FORBIDDEN_NAME_PARTS):
        return False
    if lowered.startswith("test_") or lowered.endswith("_test.py"):
        return False
    return path.is_file()


def collect_files(manifest_path: Path) -> list[Path]:
    files: set[Path] = set()
    missing: list[str] = []
    for pattern in _manifest_patterns(manifest_path):
        matches = [path for path in REPO_ROOT.glob(pattern) if _is_allowed(path)]
        if not matches:
            missing.append(pattern)
        files.update(matches)
    if missing:
        raise FileNotFoundError("Production manifest patterns without files: " + ", ".join(missing))
    return sorted(files)


def build_archive(manifest_path: Path, output_path: Path) -> tuple[int, str]:
    files = collect_files(manifest_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output_path, "w:gz") as archive:
        for path in files:
            relative = path.relative_to(REPO_ROOT)
            archive.add(path, arcname=str(Path(ARCHIVE_ROOT) / relative), recursive=False)

    digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
    output_path.with_suffix(output_path.suffix + ".sha256").write_text(
        f"{digest}  {output_path.name}\n",
        encoding="ascii",
    )
    return len(files), digest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the minimal AI Estimator production archive.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    count, digest = build_archive(args.manifest.resolve(), args.out.resolve())
    print(f"files={count}")
    print(f"archive={args.out.resolve()}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
