"""CI guard: every SKILL.md frontmatter block must be valid YAML.

An unquoted ": " inside a `description:` value silently produces invalid
frontmatter, which breaks the indexer, the CLI frontmatter parser, and any
downstream consumer. Keep this as a hard gate.

Run directly:  uv run python scripts/check_frontmatter.py
Exit codes:    0 = all valid, 1 = at least one invalid block.
"""

import glob
import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
PATTERNS = (
    "skills/**/SKILL.md",
    "canonical/**/SKILL.md",
    "collections/**/SKILL.md",
)


def main() -> int:
    paths = []
    for pattern in PATTERNS:
        paths.extend(glob.glob(str(REPO / pattern), recursive=True))

    bad = []
    for p in paths:
        text = open(p, encoding="utf-8", errors="replace").read()
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            bad.append((p, "unterminated frontmatter"))
            continue
        try:
            yaml.safe_load(text[3:end])
        except Exception as exc:  # noqa: BLE001 - report any parser failure
            bad.append((p, str(exc).splitlines()[0]))

    if bad:
        for path, err in bad:
            print(f"INVALID {path}: {err}", file=sys.stderr)
        print(f"\n{len(bad)} of {len(paths)} SKILL.md files have invalid frontmatter",
              file=sys.stderr)
        return 1

    print(f"OK: {len(paths)} SKILL.md files, all frontmatter valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())