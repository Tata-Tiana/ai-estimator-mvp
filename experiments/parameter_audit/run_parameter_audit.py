"""CLI entry point for parameter_audit."""

from __future__ import annotations

import sys
from pathlib import Path

from parameter_audit import run_audit


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python run_parameter_audit.py <case_dir>")
        return 2

    case_dir = Path(sys.argv[1]).resolve()
    outputs = run_audit(case_dir)
    print("Parameter audit completed")
    for name, path in outputs.items():
        print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

