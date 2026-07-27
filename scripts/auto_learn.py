#!/usr/bin/env python3
"""
auto_learn.py — Auto-learning pipeline to convert /learn sessions into draft skills or rules with duplicate checking.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
SKILLS_DIR = REPO_ROOT / 'skills'
RULES_DIR = REPO_ROOT / 'rules'
INDEX_FILE = REPO_ROOT / 'skills.json'


def ingest_proposal(title: str, content: str, is_rule: bool = False):
    if not INDEX_FILE.exists():
        print("skills.json not found.")
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        skills = json.load(f).get('skills', {})

    slug = title.lower().replace(' ', '-').replace('_', '-')

    # Check duplicates
    if slug in skills:
        print(f"⚠️ Duplicate detected! A skill named '{slug}' already exists at {skills[slug]['rel_path']}.")
        print("Recommendation: Merge learning proposal into existing skill rather than creating duplicate.")
        return False

    if is_rule:
        rule_file = RULES_DIR / f"{slug}.md"
        rule_content = f"""---
title: "{title}"
description: "Learned rule automatically generated via /learn pipeline"
origin: "/learn"
---

# Rule: {title}

{content}
"""
        RULES_DIR.mkdir(parents=True, exist_ok=True)
        rule_file.write_text(rule_content, encoding='utf-8')
        print(f"✅ Ingested new learned rule: {rule_file}")
    else:
        skill_dir = SKILLS_DIR / slug
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / 'SKILL.md'
        skill_content = f"""---
name: {slug}
description: "{title}"
category: "workflow"
status: "experimental"
version: "1.0.0"
---

# {title}

## Overview

{content}
"""
        skill_file.write_text(skill_content, encoding='utf-8')
        print(f"✅ Ingested new learned skill: {skill_file}")

    return True


if __name__ == '__main__':
    if len(sys.argv) > 2:
        title = sys.argv[1]
        body = sys.argv[2]
        is_r = '--rule' in sys.argv
        ingest_proposal(title, body, is_r)
    else:
        print("Usage: python3 auto_learn.py <title> <body> [--rule]")
