#!/usr/bin/env python3
"""
orchestrate.py — Dynamic orchestration engine for assembling multi-skill execution DAGs from goals.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'


def orchestrate_goal(goal: str):
    if not INDEX_FILE.exists():
        print("skills.json not found. Run build_index.py first.")
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    skills = data['skills']
    tokens = [t.lower() for t in re.findall(r'\w+', goal) if len(t) > 2]

    matched_skills = []
    for name, meta in skills.items():
        score = 0
        desc = meta['description'].lower()
        for t in tokens:
            if t in name.lower(): score += 30
            if t in desc: score += 10
        if score > 0:
            matched_skills.append((score, meta))

    matched_skills.sort(key=lambda x: x[0], reverse=True)
    selected_skills = [m[1] for m in matched_skills[:5]]

    # Collect dependencies
    all_selected = set(s['name'] for s in selected_skills)
    prereqs = set()

    for s in selected_skills:
        for dep in s.get('dependencies', []):
            if dep not in all_selected:
                prereqs.add(dep)

    print(f"\n🧠 Intelligent Orchestration Plan for Goal:\n   \"{goal}\"\n")
    print("--------------------------------------------------------------------------------")
    print("Stage 1: Prerequisite Rules & Pre-execution Controls")
    for pr in sorted(list(prereqs)):
        print(f"  [Prereq] Load `{pr}`")

    print("\nStage 2: Core Execution Skill Sequence (DAG)")
    for idx, s in enumerate(selected_skills, 1):
        print(f"  Step {idx}: Execute `{s['name']}` ({s['namespace_command']})")
        print(f"          Role: {s['description'][:80]}...")

    print("\nStage 3: Verification & Quality Gate")
    print("  [Verify] Run `verification-before-completion` & Vitest/Playwright tests")
    print("--------------------------------------------------------------------------------\n")


if __name__ == '__main__':
    goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Build secure Next.js 15 app with Supabase auth and Vitest tests"
    orchestrate_goal(goal)
