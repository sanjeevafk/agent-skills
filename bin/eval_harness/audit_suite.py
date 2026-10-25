#!/usr/bin/env python3
"""
audit_suite.py - Full 67-Skill Audit & Evaluation Test Suite
Implements Makarevych Eval Criteria across the active Antigravity runtime.
"""

import os
import re
import json
from pathlib import Path

skills_dir = Path(os.path.expanduser("~/.gemini/config/skills"))
skills = sorted([d for d in skills_dir.iterdir() if d.is_dir() or d.is_symlink()])

results = []

danger_patterns = [
    (r"curl\s+-[sS]*\s+.*?\s*\|\s*(ba)?sh", "Unvetted curl-to-bash execution"),
    (r"wget\s+.*?\s*\|\s*(ba)?sh", "Unvetted wget-to-bash execution"),
    (r"rm\s+-rf\s+[/|\$]", "Destructive recursive removal pattern"),
]

for s in skills:
    skill_file = s / "SKILL.md"
    if not skill_file.exists():
        results.append({
            "name": s.name,
            "status": "FAIL_MISSING",
            "kb": 0.0,
            "est_tokens": 0,
            "directives_count": 0,
            "density": 0.0,
            "sec_issues": ["Missing SKILL.md"]
        })
        continue

    text = skill_file.read_text(encoding="utf-8", errors="ignore")
    char_len = len(text)
    est_tokens = int(char_len / 4)
    lines = len(text.splitlines())
    kb = char_len / 1024.0

    # Check YAML frontmatter
    fm_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    has_valid_fm = False
    desc_len = 0
    if fm_match:
        fm = fm_match.group(1)
        has_name = bool(re.search(r"^name:\s*.+", fm, re.MULTILINE))
        desc_match = re.search(r"^description:\s*(.+)", fm, re.MULTILINE)
        has_desc = bool(desc_match)
        if desc_match:
            desc_len = len(desc_match.group(1).strip())
        has_valid_fm = has_name and has_desc

    # Extract testable directives
    directives = []
    for line in text.splitlines():
        line_clean = line.strip()
        if re.match(r"^[-*]\s+\*\*.*?\*\*", line_clean) or re.match(r"^\d+\.\s+\*\*.*?\*\*", line_clean):
            directives.append(line_clean)
        elif line_clean.startswith("- ") or line_clean.startswith("* ") or re.match(r"^\d+\.\s+", line_clean):
            if len(line_clean) > 20 and not line_clean.startswith("#"):
                directives.append(line_clean)

    # Security scan
    sec_issues = []
    for pat, desc_danger in danger_patterns:
        if re.search(pat, text, re.IGNORECASE):
            sec_issues.append(desc_danger)

    density = len(directives) / kb if kb > 0 else 0

    # Classification
    if not has_valid_fm:
        rating = "INVALID_SPEC"
    elif sec_issues:
        rating = "SECURITY_WARN"
    elif kb > 100:
        rating = "SUPER_HEAVY"
    elif kb > 12 and len(directives) < 5:
        rating = "VIBE_SLOP"
    else:
        rating = "PASS_OPTIMAL"

    results.append({
        "name": s.name,
        "status": rating,
        "kb": round(kb, 1),
        "est_tokens": est_tokens,
        "lines": lines,
        "directives_count": len(directives),
        "density": round(density, 1),
        "sec_issues": sec_issues
    })

# Summary output
status_counts = {}
for r in results:
    st = r["status"]
    status_counts[st] = status_counts.get(st, 0) + 1

print(json.dumps({
    "total": len(results),
    "summary": status_counts,
    "skills": results
}, indent=2))
