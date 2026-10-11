#!/usr/bin/env python3
"""
doctor.py — Comprehensive system diagnostic health inspector and skill explanation tool.
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
SKILLS_DIR = REPO_ROOT / 'skills'
RULES_DIR = REPO_ROOT / 'rules'
COMMANDS_DIR = REPO_ROOT / 'commands'
EXPORTS_DIR = REPO_ROOT / 'exports'


def run_doctor():
    print("\n🩺 Running Agent Skills System Doctor Diagnostic...\n")
    checks = []

    # 1. Index file check
    if INDEX_FILE.exists():
        checks.append(("skills.json Index", True, f"Found ({INDEX_FILE.stat().st_size:,} bytes)"))
    else:
        checks.append(("skills.json Index", False, "Missing! Run `gskills index`"))

    # 2. Canonical skills check
    if SKILLS_DIR.exists():
        skill_count = len([d for d in SKILLS_DIR.iterdir() if d.is_dir()])
        checks.append(("Skills Repository", True, f"Found {skill_count} skill directories"))
    else:
        checks.append(("Skills Repository", False, "Missing `skills/` directory"))

    # 3. Canonical rules check
    if RULES_DIR.exists():
        rule_count = len(list(RULES_DIR.rglob("*.md")))
        checks.append(("Rules Standards", True, f"Found {rule_count} rule files"))
    else:
        checks.append(("Rules Standards", False, "Missing `rules/` directory"))

    # 4. Commands directory check
    if COMMANDS_DIR.exists():
        cmd_count = len(list(COMMANDS_DIR.rglob("*.md")))
        checks.append(("Command Wrappers", True, f"Found {cmd_count} generated command wrappers"))
    else:
        checks.append(("Command Wrappers", False, "Missing `commands/` directory. Run `gskills generate-commands`"))

    # 5. Multi-client exports check
    if EXPORTS_DIR.exists():
        exp_count = len(list(EXPORTS_DIR.rglob("*")))
        checks.append(("Multi-Client Exports", True, f"Found {exp_count} export files in exports/"))
    else:
        checks.append(("Multi-Client Exports", False, "Missing `exports/` directory. Run `gskills export`"))

    # 6. Global config check
    cfg_file = Path(os.path.expanduser("~/.global-skills.conf"))
    if cfg_file.exists():
        checks.append(("Global Config (~/.global-skills.conf)", True, f"Configured"))
    else:
        checks.append(("Global Config (~/.global-skills.conf)", False, "Not found. Run `gskills init-config`"))

    all_passed = True
    for name, status, msg in checks:
        icon = "✅" if status else "❌"
        if not status: all_passed = False
        print(f"  {icon} {name:<40} : {msg}")

    print("\n--------------------------------------------------------------------------------")
    if all_passed:
        print("🎉 System Doctor Status: HEALTHY — All framework components fully operational!")
    else:
        print("⚠️ System Doctor Status: ISSUES DETECTED — Run `gskills build-all` to repair build targets.")
    print("--------------------------------------------------------------------------------\n")
    if not all_passed:
        sys.exit(1)


def explain_skill(skill_name: str):
    if not INDEX_FILE.exists():
        print("skills.json not found. Run build_index.py first.")
        sys.exit(1)

    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Failed to read skills.json: {e}", file=sys.stderr)
        sys.exit(1)
    skills = index_data.get('skills', {})

    if skill_name not in skills:
        # Check alias
        aliases = index_data.get('aliases', {})
        if skill_name in aliases:
            skill_name = aliases[skill_name]
        else:
            print(f"Skill or alias '{skill_name}' not found.")
            sys.exit(1)

    s = skills[skill_name]
    print(f"\n📖 Skill Explanation: {s['name']}\n")
    print(f"  • Category         : {s['category_label']} ({s['category']})")
    print(f"  • Namespace Command: {s['namespace_command']}")
    print(f"  • Flat Command     : {s['flat_command']}")
    print(f"  • Description      : {s['description']}")
    print(f"  • Version / Date   : v{s['version']} (Updated: {s['last_updated']})")
    print(f"  • Tags             : {', '.join(s['tags'])}")
    print(f"  • Dependencies     : {', '.join(s['dependencies']) if s['dependencies'] else 'None'}")
    print(f"  • Est. Tokens      : {s['estimated_tokens']:,} tokens")
    print(f"  • Source File      : {s['rel_path']}\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'explain' and len(sys.argv) > 2:
            explain_skill(sys.argv[2])
        else:
            run_doctor()
    else:
        run_doctor()
