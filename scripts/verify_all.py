#!/usr/bin/env python3
"""Run the repository's complete dependency-light verification suite."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(label: str, command: list[str]) -> None:
    print(f"== {label} ==")
    result = subprocess.run(command, cwd=ROOT, text=True)
    if result.returncode:
        raise SystemExit(result.returncode)


def main() -> None:
    run("skill validation", [sys.executable, "scripts/validate_skills.py"])
    run("skill tests", [sys.executable, "scripts/test_skills.py"])
    run("integration tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"])
    run("shell syntax", ["bash", "-c", "for f in scripts/*.sh; do bash -n \"$f\" || exit 1; done"])
    run("python compilation", [sys.executable, "-m", "compileall", "-q", "scripts", "hooks"])
    print("Verification complete.")


if __name__ == "__main__":
    main()
