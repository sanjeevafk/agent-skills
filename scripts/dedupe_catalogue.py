#!/usr/bin/env python3
"""
dedupe_catalogue.py — detect and register near-duplicate skill entries.

Motivation
----------
Nine pairs of catalogue skills embed to cosine >= 0.95, seven of them at
exactly 1.000 (byte-identical descriptions). Every one of those pairs is an
accidental alias: the same skill registered twice under a short name and a
`huggingface-` prefixed name. They are unresolvable by any retriever, because
two entries carrying identical text cannot be ranked against each other; the
router either wins arbitrarily or, worse, the wrong one.

Policy: never delete
--------------------
Both entries remain on disk and in `skills.json`. The *routable* catalogue
collapses to one representative per duplicate group, chosen deterministically:

  1. prefer the member present in the canonical (production) tier, so the
     active skill set is preserved;
  2. otherwise prefer the shorter name, which is the stable public handle;
  3. break remaining ties lexicographically.

The other member is registered in the index's existing top-level `aliases` map,
so `hf-mem` still resolves to `huggingface-mem` (or vice versa) for any caller
that consults aliases, and the full 531-entry catalogue remains available to
tooling that wants it.

Writes
------
  skills.json            aliases map extended; duplicate members marked
  skills_canonical.json  the routable subset actually embedded for routing
  benchmarks/dedup_report.json

Usage:
    uv run python scripts/dedupe_catalogue.py            # apply
    uv run python scripts/dedupe_catalogue.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
INDEX_FILE = REPO / "skills.json"
NPY_FILE = REPO / "skills_embeddings.npy"
MANIFEST_FILE = REPO / "skills_manifest.json"
CANONICAL_FILE = REPO / "skills_canonical.json"
REPORT_FILE = REPO / "benchmarks" / "dedup_report.json"

DUPLICATE_COSINE = 0.95


def canonical_tier() -> set[str]:
    canonical = REPO / "canonical"
    if not canonical.exists():
        return set()
    return {p.name for p in canonical.iterdir() if p.is_dir()}


def find_groups(names: list[str], vectors: np.ndarray, threshold: float) -> list[list[str]]:
    """Group names whose embeddings are mutually near-identical.

    Uses single-linkage over the threshold graph so a chain of near-identical
    entries collapses into one group rather than several overlapping pairs.
    """
    sims = vectors @ vectors.T
    parent = list(range(len(names)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if sims[i, j] >= threshold:
                union(i, j)

    groups: dict[int, list[str]] = defaultdict(list)
    for i, name in enumerate(names):
        groups[find(i)].append(name)
    return [sorted(g) for g in groups.values() if len(g) > 1]


def representative(group: list[str], canonical: set[str]) -> str:
    in_canonical = [n for n in group if n in canonical]
    pool = in_canonical or group
    return min(pool, key=lambda n: (len(n), n))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=DUPLICATE_COSINE)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not NPY_FILE.exists() or not MANIFEST_FILE.exists():
        print("error: embedding cache missing; run scripts/build_index.py and "
              "scripts/build_skill_embeddings.py first", file=sys.stderr)
        return 1

    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    vectors = np.load(NPY_FILE)

    names = [e["name"] for e in manifest["skills"]]
    if vectors.shape[0] != len(names):
        print("error: vector/manifest mismatch; rebuild embeddings", file=sys.stderr)
        return 1

    canonical = canonical_tier()
    groups = find_groups(names, vectors, args.threshold)

    aliases: dict[str, str] = dict(index.get("aliases", {}))
    resolved: dict[str, str] = {}
    report_groups = []

    for group in sorted(groups):
        rep = representative(group, canonical)
        members = [m for m in group if m != rep]
        for m in members:
            # Never clobber an existing alias that points somewhere else.
            if m not in aliases:
                aliases[m] = rep
            resolved[m] = rep
        report_groups.append({"representative": rep, "absorbed": members})
        print(f"  {rep}")
        for m in members:
            print(f"      +-> {m}")

    if not report_groups:
        print(f"no duplicate groups at cosine >= {args.threshold}")
        return 0

    print(f"\n{len(report_groups)} duplicate group(s); "
          f"{len(resolved)} name(s) collapsed to a representative")
    print(f"full catalogue {len(names)} -> routable {len(names) - len(resolved)}")

    if args.dry_run:
        print("\nDRY RUN: nothing written.")
        return 0

    index["aliases"] = aliases
    # mark absorbed entries so consumers can see the grouping without aliases
    for g in report_groups:
        for m in g["absorbed"]:
            if m in index["skills"]:
                index["skills"][m]["duplicate_of"] = g["representative"]
    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")

    canonical_skills = {
        n: v for n, v in index["skills"].items() if n not in resolved
    }
    CANONICAL_FILE.write_text(
        json.dumps(
            {
                "generated_utc": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat(),
                "source": "skills.json",
                "duplicate_threshold": args.threshold,
                "total_in_index": len(index["skills"]),
                "routable_count": len(canonical_skills),
                "collapsed": resolved,
                "skills": canonical_skills,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    REPORT_FILE.write_text(
        json.dumps(
            {
                "threshold": args.threshold,
                "catalogue_size": len(names),
                "groups": report_groups,
                "collapsed_count": len(resolved),
                "routable_count": len(names) - len(resolved),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nwrote {INDEX_FILE.name}, {CANONICAL_FILE.name}, "
          f"{REPORT_FILE.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())