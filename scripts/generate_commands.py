#!/usr/bin/env python3
"""
generate_commands.py — Auto-generate namespaced & backward-compatible flat command wrappers.
"""

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
SKILLS_DIR = REPO_ROOT / 'skills'
COMMANDS_DIR = REPO_ROOT / 'commands'
INDEX_FILE = REPO_ROOT / 'skills.json'

WRAPPER_TEMPLATE = """\
<!-- AUTO-GENERATED FILE — DO NOT EDIT MANUALLY -->
<!-- Source of truth: {rel_path} -->
---
description: "{description}"
category: "{category}"
namespace: "{namespace_cmd}"
flat_command: "{flat_command}"
---

# Command: {name} ({namespace_cmd})

> **Trigger**: {description}
> **Category**: {category_label}
> **Source Skill**: [{rel_path}](file://{abs_path})

---

{body}
"""


def generate_commands():
    if not INDEX_FILE.exists():
        print("skills.json not found. Building index first...")
        import subprocess
        subprocess.run([sys.executable, str(REPO_ROOT / 'scripts' / 'build_index.py')], check=True)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    skills = index_data['skills']

    # Clean existing commands directory
    if COMMANDS_DIR.exists():
        shutil.rmtree(COMMANDS_DIR)
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    count_namespaced = 0
    count_flat = 0
    count_aliases = 0

    for name, meta in skills.items():
        rel_path = meta['rel_path']
        abs_path = str(REPO_ROOT / rel_path)
        skill_file = REPO_ROOT / rel_path

        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding='utf-8')
        # Strip frontmatter for body preview
        if content.startswith('---'):
            end = content.find('\n---', 3)
            if end != -1:
                body = content[end + 4:].strip()
            else:
                body = content.strip()
        else:
            body = content.strip()

        desc_escaped = meta['description'].replace('"', '\\"')

        wrapper_content = WRAPPER_TEMPLATE.format(
            name=name,
            description=desc_escaped,
            category=meta['category'],
            category_label=meta['category_label'],
            namespace_cmd=meta['namespace_command'],
            flat_command=meta['flat_command'],
            rel_path=rel_path,
            abs_path=abs_path,
            body=body,
        )

        # 1. Write namespaced command: /category/short_name
        parts = meta['namespace_command'].strip('/').split('/')
        if len(parts) == 2:
            cat_dir = COMMANDS_DIR / parts[0]
            cat_dir.mkdir(parents=True, exist_ok=True)
            cmd_file = cat_dir / f"{parts[1]}.md"
            cmd_file.write_text(wrapper_content, encoding='utf-8')
            count_namespaced += 1

        # 2. Write backward-compatible flat command: /name.md
        flat_file = COMMANDS_DIR / f"{name}.md"
        flat_file.write_text(wrapper_content, encoding='utf-8')
        count_flat += 1

    # 3. Write explicit alias wrappers
    for alias_name, target_name in index_data.get('aliases', {}).items():
        if target_name in skills:
            target_meta = skills[target_name]
            alias_file = COMMANDS_DIR / f"{alias_name}.md"
            alias_content = f"""\
<!-- AUTO-GENERATED ALIAS WRAPPER — DO NOT EDIT MANUALLY -->
<!-- Alias for: {target_name} ({target_meta['namespace_command']}) -->
---
description: "Alias for {target_name}: {target_meta['description']}"
alias_target: "{target_name}"
---

# Command Alias: /{alias_name}

> **Target Command**: `{target_meta['flat_command']}` (`{target_meta['namespace_command']}`)
> **Description**: {target_meta['description']}

---

*(See `{target_meta['flat_command']}` or `skills/{target_name}/SKILL.md` for full implementation.)*
"""
            alias_file.write_text(alias_content, encoding='utf-8')
            count_aliases += 1

    
    # 4. Write Rule Commands (/rule/rule_name)
    rules_dir = REPO_ROOT / 'rules'
    rule_cmd_dir = COMMANDS_DIR / 'rule'
    rule_cmd_dir.mkdir(parents=True, exist_ok=True)
    count_rules = 0

    if rules_dir.exists():
        for rf in sorted(list(rules_dir.rglob('*.md'))):
            rname = rf.stem
            rel_p = str(rf.relative_to(REPO_ROOT))
            abs_p = str(rf.resolve())
            r_content = rf.read_text(encoding='utf-8').strip()

            rule_wrapper = f"""<!-- AUTO-GENERATED RULE COMMAND — DO NOT EDIT MANUALLY -->
<!-- Source of truth: {rel_p} -->
---
description: "Rule: {rname}"
category: "rule"
namespace: "/rule/{rname}"
flat_command: "/rule-{rname}"
---

# Rule Command: /rule/{rname}

> **Source Rule File**: [{rel_p}](file://{abs_p})

---

{r_content}
"""
            (rule_cmd_dir / f"{rname}.md").write_text(rule_wrapper, encoding='utf-8')
            (COMMANDS_DIR / f"rule-{rname}.md").write_text(rule_wrapper, encoding='utf-8')
            count_rules += 1

    print(f"Generated {count_namespaced} namespaced commands, {count_flat} flat commands, {count_rules} rule commands, and {count_aliases} aliases in {COMMANDS_DIR}")



if __name__ == '__main__':
    generate_commands()
