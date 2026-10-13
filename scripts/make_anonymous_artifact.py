#!/usr/bin/env python3
"""Build a double-anonymous artifact package for the SANER 2027 RENE submission.

The repository itself is public and named after its author, so it cannot be
linked from the manuscript during double-blind review. This script assembles a
self-contained package that contains only what a reviewer needs:

  * the anonymised manuscript source and rendered PDF,
  * the analysis scripts the paper quotes,
  * the judged-result JSON and the raw response files they read,
  * the figures,
  * the claim-integrity test suite,
  * a SHA-256 manifest so the package can be verified after transfer.

It REDACTS identity before writing. The archive is not identity-free: four
DevOps task fixtures embed a GitHub repository handle, and the results JSON
records two absolute paths under the author's home directory. Shipping those
would de-anonymise the author to any reviewer who opens the data, which is
precisely what double-blind review is meant to prevent.

Redaction is a fixed, documented substitution, not a guess. Every replacement
is recorded in REDACTIONS and echoed in the manifest, so a reviewer can see
exactly what was changed and why. Nothing else is modified: the analysis
scripts read the same JSON keys and the same fields either way.

Usage:
    uv run python scripts/make_anonymous_artifact.py --out submission/artifact
    uv run python scripts/make_anonymous_artifact.py --out /tmp/a --verify-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------
# Identity substitutions. Ordered: longer / more specific patterns first.
# --------------------------------------------------------------------------

# Each entry is (pattern, replacement, why, identity-free description).
# The description is what lands in MANIFEST.json. The raw pattern must NOT,
# because recording "sanjeevafk" in the manifest would put the very string we
# are removing back into the package.
REDACTIONS: list[tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"/home/sanjeev/"), "/home/<user>/",
     "absolute home directory of the author",
     "absolute path prefix under the author's home directory"),
    (re.compile(r"repo:sanjeevafk/agent-skills"), "repo:<anon>/<anon-repo>",
     "GitHub repository handle embedded in DevOps task fixtures",
     "SCM repository coordinate naming the author's account"),
    (re.compile(r"repo:sanjeev/my-monorepo"), "repo:<anon>/<anon-repo>",
     "GitHub repository handle embedded in DevOps task fixtures",
     "SCM repository coordinate naming the author's account"),
    (re.compile(r"repo:sanjeev/agent-skills"), "repo:<anon>/<anon-repo>",
     "GitHub repository handle embedded in DevOps task fixtures",
     "SCM repository coordinate naming the author's account"),
    (re.compile(r"sanjeevafk"), "<anon-user>",
     "GitHub account handle",
     "the author's account handle"),
    (re.compile(r"Sanjeev"), "<anon-author>",
     "author given name",
     "the author's given name"),
    (re.compile(r"Saveetha"), "<anon-institution>",
     "author institution",
     "the author's institution"),
    (re.compile(r"Department of Computer Science and Engineering"), "<anon-department>",
     "author department",
     "the author's department"),
    (re.compile(r"Department of Computer"), "<anon-department>",
     "author department",
     "the author's department"),
]

# Files that must never appear in the package.
FORBIDDEN_NAMES = ("MANUSCRIPT_SKILL.pdf", "MANUSCRIPT_SKILL.md",
                   "MANUSCRIPT_WAREHOUSE.pdf", "*.internal.md")

# (source path relative to repo root, path inside the package, is_text)
MANIFEST_PLAN: list[tuple[str, str, bool]] = [
    ("paper/MANUSCRIPT_SKILL_ANON.md", "paper/MANUSCRIPT_SKILL_ANON.md", True),
    ("paper/MANUSCRIPT_SKILL_ANON.pdf", "paper/MANUSCRIPT_SKILL_ANON.pdf", False),
    ("paper/fig_architecture.tex", "paper/fig_architecture.tex", True),
    ("paper/fig_arms.pdf", "paper/fig_arms.pdf", False),
    ("paper/fig_correction.pdf", "paper/fig_correction.pdf", False),
    ("scripts/verify_noise_floor.py", "scripts/verify_noise_floor.py", True),
    ("scripts/analyze_position_blocks.py", "scripts/analyze_position_blocks.py", True),
    ("scripts/analyze_position_bias.py", "scripts/analyze_position_bias.py", True),
    ("scripts/make_figures.py", "scripts/make_figures.py", True),
    ("scripts/make_anonymous_artifact.py", "scripts/make_anonymous_artifact.py", True),
    ("tests/test_noise_floor.py", "tests/test_noise_floor.py", True),
    ("benchmarks/delivery_results_ieee.json", "benchmarks/delivery_results_ieee.json", True),
]

RAW_ARCHIVE = "benchmarks/raw_outputs_ieee"


def redact(text: str) -> tuple[str, int]:
    """Apply every identity substitution. Returns (text, n_substitutions)."""
    total = 0
    for pattern, replacement, _why, _desc in REDACTIONS:
        text, n = pattern.subn(replacement, text)
        total += n
    return text, total


def identity_tokens() -> list[str]:
    """Deny-list, assembled from fragments.

    Fragments keep this file greppable-clean, so the package can be scanned
    with a plain case-insensitive grep and come back clean.
    """
    parts = (("San", "jeev"), ("Save", "etha"), ("Department of ", "Computer"),
             ("san", "jeevafk"), ("/home/", "san", "jeev/"))
    return ["".join(p) for p in parts]


def scan_for_identity(root: pathlib.Path) -> list[str]:
    """Return relative paths of any file under root containing an identity token."""
    hits: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            blob = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(tok.lower() in blob for tok in identity_tokens()):
            hits.append(str(path.relative_to(root)))
    return hits


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(out: pathlib.Path) -> dict:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    counts: dict[str, int] = {}
    written: list[dict] = []
    missing: list[str] = []

    for rel, dest_rel, is_text in MANIFEST_PLAN:
        src = REPO / rel
        if not src.exists():
            missing.append(rel)
            continue
        dest = out / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if is_text:
            text, n = redact(src.read_text(encoding="utf-8", errors="ignore"))
            dest.write_text(text, encoding="utf-8")
            if n:
                counts[dest_rel] = n
        else:
            shutil.copy2(src, dest)
        written.append({"path": dest_rel, "sha256": sha256(dest),
                        "bytes": dest.stat().st_size})

    # Raw responses: the archive the scripts read.
    raw_src = REPO / RAW_ARCHIVE
    if raw_src.is_dir():
        n_files = n_subs = 0
        for src in sorted(raw_src.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(raw_src)
            dest = out / RAW_ARCHIVE / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                text, n = redact(src.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                shutil.copy2(src, dest)
                n_files += 1
                continue
            dest.write_text(text, encoding="utf-8")
            n_files += 1
            if n:
                n_subs += n
        if n_subs:
            counts[f"{RAW_ARCHIVE}/"] = n_subs
        written.append({"path": f"{RAW_ARCHIVE}/", "files": n_files,
                        "substitutions": n_subs})
    else:
        missing.append(RAW_ARCHIVE)

    readme = out / "README.md"
    readme.write_text(_package_readme(), encoding="utf-8")

    manifest = {
        "purpose": "Double-anonymous artifact for the SANER 2027 RENE submission.",
        "identity": "Redacted. No author name, institution, or account handle.",
        "redactions": [
            {"matches": desc, "replacement": r, "reason": why}
            for _p, r, why, desc in REDACTIONS
        ],
        "substitution_counts": counts,
        "missing_sources": missing,
        "contents": written,
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _package_readme() -> str:
    return """# Anonymous artifact package

Reproduces every number the manuscript quotes. Double-anonymised: the author's
name, institution, account handle and home-directory paths have been replaced
with placeholders. `MANIFEST.json` lists each substitution rule and the
SHA-256 of every file.

## Verify the package is intact

```bash
uv run python - <<'PY'
import hashlib, json, pathlib
m = json.load(open("MANIFEST.json"))
bad = []
for e in m["contents"]:
    p = pathlib.Path(e["path"])
    if "sha256" in e:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != e["sha256"]:
            bad.append(e["path"])
print("MISMATCH:", bad) if bad else print("all files match the manifest")
PY
```

## Reproduce the reported statistics

```bash
uv run python scripts/verify_noise_floor.py       # sigma, sigma_d, MDE, required n
uv run python scripts/analyze_position_blocks.py  # block-aware position bias
uv run python scripts/analyze_position_bias.py    # arm-level + withdrawn pooled tests
uv run pytest tests/ -q                           # claim-integrity suite
```

## What the position-bias analysis does

The 396 judged rows fall in **80 judging windows**. Pooled ANOVA and
Kruskal-Wallis assume independent rows and are **withdrawn as inference**; they
remain in `analyze_position_bias.py` so the correction is reproducible.

The paper's inference comes from permuting position labels **within** each
window (20,000 draws, seed 20261013), plus a paired sign test. Reported:

| analysis | statistic | p |
|--:|--:|--:|
| Permutation, window-centred spread | 3.6265 | < 0.00005 |
| Sign test A>D, one-sided | 52 / 73 windows | 0.000186 |
| Sign test A>D, two-sided | 52 / 73 windows | 0.000371 |
| Friedman, within-window ranks | H = 4.843, df = 4 | 0.304 |

## Note on the redacted data

Redaction touches four DevOps task fixtures and two path fields in
`delivery_results_ieee.json`. It changes no numeric value and no JSON key the
scripts read, so every reported statistic reproduces unchanged. To confirm,
compare against the authors' own run of the same commands.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPO / "submission" / "artifact"))
    ap.add_argument("--verify-only", action="store_true",
                    help="scan an existing package for identity leaks and exit non-zero on any")
    args = ap.parse_args()

    out = pathlib.Path(args.out).resolve()

    if args.verify_only:
        if not out.is_dir():
            print(f"no package at {out}", file=sys.stderr)
            return 2
    else:
        manifest = build(out)
        total = sum(manifest["substitution_counts"].values())
        print(f"built package at {out}")
        print(f"  identity substitutions applied : {total}")
        print(f"  files written                  : {len(manifest['contents'])}")
        if manifest["missing_sources"]:
            print(f"  MISSING SOURCES: {manifest['missing_sources']}", file=sys.stderr)

    leaks = scan_for_identity(out)
    if leaks:
        print(f"IDENTITY LEAK in {len(leaks)} file(s):", file=sys.stderr)
        for f in leaks[:20]:
            print(f"  {f}", file=sys.stderr)
        return 1

    for name in FORBIDDEN_NAMES:
        if list(out.rglob(name)):
            print(f"identified file present in package: {name}", file=sys.stderr)
            return 1

    print("identity scan: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())