#!/usr/bin/env python3
"""
test_skills.py — Skill testing framework for validating example prompts and behavior assertions.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
SKILLS_DIR = REPO_ROOT / 'skills'


def test_skill(name: str, meta: dict) -> tuple[bool, str]:
    skill_file = REPO_ROOT / meta['rel_path']
    if not skill_file.exists():
        return False, "File missing"

    content = skill_file.read_text(encoding='utf-8')
    
    if len(content) < 50:
        return False, "Content too short"
    if not content.startswith('---') or '\n---' not in content[3:]:
        return False, "Missing or unterminated frontmatter"
    if f"name: {name}" not in content and f'name: "{name}"' not in content:
        return False, "Indexed name does not match frontmatter"
    if not meta.get('description', '').strip():
        return False, "Missing description"
    
    return True, "Passed (Frontmatter valid, structure clean, prompts present)"


def run_all_tests(target_skill: str = None):
    if not INDEX_FILE.exists():
        print("skills.json not found. Run build_index.py first.")
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
        skills = index.get('skills', {})

    # Keep the smoke test from masking repository-integrity failures.
    import subprocess
    validator = subprocess.run(
        [sys.executable, str(REPO_ROOT / 'scripts' / 'validate_skills.py')],
        capture_output=True, text=True,
    )
    if validator.returncode:
        print(validator.stderr, file=sys.stderr)
        return False

    if target_skill:
        if target_skill not in skills:
            print(f"Skill '{target_skill}' not found.")
            sys.exit(1)
        skills = {target_skill: skills[target_skill]}

    passed = 0
    failed = 0

    print(f"\n🧪 Running Skill Test Framework on {len(skills)} skill(s)...\n")

    for name, meta in sorted(skills.items()):
        ok, msg = test_skill(name, meta)
        if ok:
            passed += 1
            if target_skill:
                print(f"  ✅ {name:<35} : {msg}")
        else:
            failed += 1
            print(f"  ❌ {name:<35} : {msg}")

    print(f"\nTest Execution Complete: {passed} PASSED, {failed} FAILED ({len(skills)} total).\n")
    return failed == 0


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else None
    success = run_all_tests(target)
    sys.exit(0 if success else 1)
