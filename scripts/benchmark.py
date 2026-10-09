#!/usr/bin/env python3
"""Repeatable build-performance benchmark for the skill framework."""

import argparse
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def measure(command: list[str], repeats: int) -> list[float]:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        samples.append((time.perf_counter() - start) * 1000)
    return samples


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmark-results.json")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")

    commands = {
        "validate_skills_ms": [sys.executable, "scripts/validate_skills.py"],
        "build_index_ms": [sys.executable, "scripts/build_index.py"],
        "generate_commands_ms": [sys.executable, "scripts/generate_commands.py"],
        "generate_docs_ms": [sys.executable, "scripts/generate_docs.py"],
        "integration_tests_ms": [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
    }
    results = {}
    for name, command in commands.items():
        samples = measure(command, args.repeats)
        results[name] = {
            "samples": [round(value, 2) for value in samples],
            "median": round(statistics.median(samples), 2),
            "min": round(min(samples), 2),
            "max": round(max(samples), 2),
        }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skills": len(list((ROOT / "skills").rglob("SKILL.md"))),
        "repeats": args.repeats,
        "metrics": results,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
