#!/usr/bin/env python3
"""
playbooks.py — Manage, compose, and generate command wrappers for capability playbooks.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
PLAYBOOKS_DIR = REPO_ROOT / 'playbooks'
COMMANDS_DIR = REPO_ROOT / 'commands'
INDEX_FILE = REPO_ROOT / 'skills.json'

DEFAULT_PLAYBOOKS = {
    "senior-engineer": {
        "name": "Senior Engineer Playbook",
        "description": "Rigorous full-stack engineering workflow: Systematic Debugging + Clean Architecture + TDD + Senior Reviewer",
        "category": "playbook",
        "skills": ["systematic-debugging", "code-reviewer", "tdd-workflow", "verification-before-completion"],
        "rules": ["clean-architecture", "clean-code", "user-global-rules"],
        "agents": ["gsd-planner", "gsd-executor"]
    },
    "security-audit": {
        "name": "Security & Vulnerability Audit Playbook",
        "description": "Comprehensive security assessment: Code Security Review + Vulnerability Scan + Gateguard + Tirith Policies",
        "category": "playbook",
        "skills": ["security-review", "security-scan", "gateguard", "security-bounty-hunter", "healthcare-phi-compliance"],
        "rules": ["release-it", "user-global-rules"],
        "agents": ["gsd-nyquist-auditor"]
    },
    "fullstack-nextjs": {
        "name": "Fullstack Next.js + Supabase Stack",
        "description": "Next.js 15 App Router + Supabase RLS + Tailwind & Radix UI + Vitest & Playwright E2E",
        "category": "playbook",
        "skills": ["nextjs-15-expert", "supabase-expert", "tailwind-radix-expert", "fullstack-feature-scaffold", "e2e-testing"],
        "rules": ["clean-architecture", "designing-data-intensive-applications"],
        "agents": ["gsd-planner", "gsd-executor"]
    },
    "mvp-bootstrap": {
        "name": "MVP Bootstrap & Phase Execution Playbook",
        "description": "Rapid tracer-bullet MVP scaffolding and GSD wave execution with Nyquist verification",
        "category": "playbook",
        "skills": ["orch-build-mvp", "gsd-new-project", "gsd-plan-phase", "gsd-execute-phase", "gsd-verify-work"],
        "rules": ["the-pragmatic-programmer", "user-global-rules"],
        "agents": ["gsd-planner", "gsd-executor", "gsd-verifier"]
    }
}


def ensure_default_playbooks():
    PLAYBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    for pb_id, data in DEFAULT_PLAYBOOKS.items():
        pb_file = PLAYBOOKS_DIR / f"{pb_id}.json"
        if not pb_file.exists():
            pb_file.write_text(json.dumps(data, indent=2), encoding='utf-8')


def generate_playbook_commands():
    ensure_default_playbooks()
    compose_dir = COMMANDS_DIR / 'compose'
    stack_dir = COMMANDS_DIR / 'stack'
    compose_dir.mkdir(parents=True, exist_ok=True)
    stack_dir.mkdir(parents=True, exist_ok=True)

    pb_files = list(PLAYBOOKS_DIR.glob('*.json'))
    count = 0

    for pbf in pb_files:
        try:
            with open(pbf, 'r', encoding='utf-8') as f:
                pb = json.load(f)
        except Exception:
            continue

        pb_id = pbf.stem
        name = pb.get('name', pb_id)
        desc = pb.get('description', '')
        skills = pb.get('skills', [])
        rules = pb.get('rules', [])
        agents = pb.get('agents', [])

        wrapper_content = f"""<!-- AUTO-GENERATED PLAYBOOK COMMAND — DO NOT EDIT MANUALLY -->
<!-- Source: playbooks/{pb_id}.json -->
---
description: "Playbook: {name} — {desc}"
category: "playbook"
namespace: "/compose/{pb_id}"
flat_command: "/stack-{pb_id}"
---

# Capability Playbook: {name}

> **Description**: {desc}
> **Command Triggers**: `/compose/{pb_id}` or `/stack-{pb_id}`

---

## 🎯 Composed Capabilities & Execution Sequence

### Included Skills ({len(skills)})
{chr(10).join(f"- `{s}`" for s in skills)}

### Always-On Rules ({len(rules)})
{chr(10).join(f"- `{r}`" for r in rules)}

### Specialized Subagents ({len(agents)})
{chr(10).join(f"- `{a}`" for a in agents)}

---

## 🚀 Execution Strategy
When this playbook is invoked, the AI agent will sequentially load and enforce all prerequisite skills, rules, and subagents specified above in dependency order.
"""

        (compose_dir / f"{pb_id}.md").write_text(wrapper_content, encoding='utf-8')
        (stack_dir / f"{pb_id}.md").write_text(wrapper_content, encoding='utf-8')
        (COMMANDS_DIR / f"compose-{pb_id}.md").write_text(wrapper_content, encoding='utf-8')
        (COMMANDS_DIR / f"stack-{pb_id}.md").write_text(wrapper_content, encoding='utf-8')
        count += 1

    print(f"Generated commands for {count} playbooks in /compose/ and /stack/ namespaces.")


if __name__ == '__main__':
    generate_playbook_commands()
