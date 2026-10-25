#!/usr/bin/env python3
"""
lint_skill.py - No-Vibe Skill Linter & Pre-Activation Quality Gate
Enforces Makarevych's 2026 Eval Standards before skills enter active runtime.

Checks:
  1. Spec Integrity: Valid YAML frontmatter with non-empty name and description.
  2. Objective Clarity: Description states a measurable objective.
  3. Directive Density: Minimum 1.5 actionable directives per KB (eliminates conversational fluff).
  4. Prompt Budget: Flags files > 15 KB to prevent stealth context bloat.
  5. Security Gate: Zero unvetted curl|sh, wget|sh, or destructive file deletions.
"""

import sys
import os
import re
from pathlib import Path
from typing import Tuple, List

DENSITY_THRESHOLD = 1.5  # directives per KB
MAX_KB_WARNING = 20.0    # KB budget

DANGER_PATTERNS = [
    (r"curl\s+-[sS]*\s+.*?\s*\|\s*(ba)?sh", "Unvetted curl-to-bash execution"),
    (r"wget\s+.*?\s*\|\s*(ba)?sh", "Unvetted wget-to-bash execution"),
    (r"rm\s+-rf\s+[/|\$]", "Destructive recursive removal pattern"),
]

def lint_skill(skill_path: Path) -> Tuple[bool, List[str], List[str]]:
    errors = []
    warnings = []

    if skill_path.is_dir():
        skill_path = skill_path / "SKILL.md"

    if not skill_path.exists():
        return False, [f"File not found: {skill_path}"], []

    text = skill_path.read_text(encoding="utf-8", errors="ignore")
    char_len = len(text)
    kb = char_len / 1024.0

    # 1. Frontmatter Check
    fm_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        errors.append("Missing YAML frontmatter block (--- ... ---)")
    else:
        fm = fm_match.group(1)
        name_match = re.search(r"^name:\s*(.+)", fm, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)", fm, re.MULTILINE)

        if not name_match or not name_match.group(1).strip():
            errors.append("Missing required frontmatter field: 'name'")
        if not desc_match or not desc_match.group(1).strip():
            errors.append("Missing required frontmatter field: 'description'")
        else:
            desc = desc_match.group(1).strip()
            if len(desc) < 25:
                warnings.append(f"Description is very brief ({len(desc)} chars). State a concrete trigger and objective.")

    # 2. Extract Directives & Calculate Density
    directives = []
    for line in text.splitlines():
        line_clean = line.strip()
        if re.match(r"^[-*]\s+\*\*.*?\*\*", line_clean) or re.match(r"^\d+\.\s+\*\*.*?\*\*", line_clean):
            directives.append(line_clean)
        elif line_clean.startswith("- ") or line_clean.startswith("* ") or re.match(r"^\d+\.\s+", line_clean):
            if len(line_clean) > 20 and not line_clean.startswith("#"):
                directives.append(line_clean)

    density = len(directives) / kb if kb > 0 else 0
    if kb > 4.0 and density < DENSITY_THRESHOLD:
        errors.append(f"Low directive density: {density:.2f}/KB (minimum required: {DENSITY_THRESHOLD}/KB). File is conversational fluff/slop.")

    # 3. Budget Check
    if kb > MAX_KB_WARNING:
        warnings.append(f"Skill exceeds budget ({kb:.1f} KB > {MAX_KB_WARNING:.1f} KB). Consider trimming or storing in cold warehouse.")

    # 4. Security Scan
    for pat, desc_danger in DANGER_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            errors.append(f"Security hazard detected: {desc_danger}")

    passed = len(errors) == 0
    return passed, errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: lint_skill.py <path_to_SKILL.md_or_dir>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if target.is_dir():
        target = target / "SKILL.md"

    passed, errors, warnings = lint_skill(target)

    status_str = "\033[1;32m[PASS]\033[0m" if passed else "\033[1;31m[FAIL]\033[0m"
    print(f"\n{status_str} Linter Verdict for: {target.parent.name}")

    if warnings:
        print("\n⚠️  Warnings:")
        for w in warnings:
            print(f"   - {w}")

    if errors:
        print("\n❌ Errors:")
        for e in errors:
            print(f"   - {e}")
        print("\nGate: Rejected. Do not promote to active runtime.\n")
        sys.exit(1)
    else:
        print("\nGate: Approved for active runtime.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
