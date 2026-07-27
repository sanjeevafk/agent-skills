#!/usr/bin/env python3
"""
build_index.py — Parse all skills, normalize metadata, and generate skills.json.
"""

import json
import re
import sys
from pathlib import Path

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

REPO_ROOT = Path(__file__).parent.parent.resolve()
SKILLS_DIR = REPO_ROOT / 'skills'
INDEX_FILE = REPO_ROOT / 'skills.json'

CATEGORY_MAP = {
    'gsd': 'GSD Project Management',
    'debug': 'Debugging & Diagnostics',
    'web': 'Web & Frontend Development',
    'lang': 'Programming Languages & Systems',
    'style': 'Coding Style & Architecture Standards',
    'devops': 'DevOps, CI/CD & Deployment',
    'security': 'Security, Compliance & Hardening',
    'data': 'Databases & Data Engineering',
    'ai-ml': 'AI Engineering, Evals & Agents',
    'observability': 'Observability & Monitoring',
    'workflow': 'Engineering Workflows & Process',
}

ALIAS_MAP = {
    'noslop': 'no-ai-slop',
    'no-slop': 'no-ai-slop',
    'google-ts': 'google-style-typescript',
    'google-cpp': 'google-style-cpp',
    'google-java': 'google-style-java',
    'google-go': 'google-style-go',
    'google-js': 'google-style-javascript',
    'google-python': 'google-style-python',
    'google-eng': 'google-eng-practices',
    'i-have-adhd': 'adhd',
    'nasa': 'nasa-jpl-power-of-ten-python',
    'nasa-jpl': 'nasa-jpl-power-of-ten-python',
    'systematic-debug': 'systematic-debugging',
    'nextjs': 'nextjs-15-expert',
    'supabase': 'supabase-expert',
    'tailwind': 'tailwind-radix-expert',
}


def strip_frontmatter(content: str) -> tuple[dict, str]:
    meta: dict = {}
    if not content.startswith('---'):
        return meta, content
    end = content.find('\n---', 3)
    if end == -1:
        return meta, content
    frontmatter_raw = content[3:end]
    body = content[end + 4:].lstrip('\n')

    if _HAS_YAML:
        try:
            parsed = yaml.safe_load(frontmatter_raw)
            meta = parsed if isinstance(parsed, dict) else {}
        except Exception:
            pass
    else:
        for line in frontmatter_raw.splitlines():
            if ':' in line and not line.startswith(' '):
                key, _, val = line.partition(':')
                meta[key.strip()] = val.strip()

    return meta, body


def infer_category(sname: str, desc: str, body: str) -> str:
    s = (sname + ' ' + desc + ' ' + body[:300]).lower()
    if sname.startswith('gsd-'):
        return 'gsd'
    if sname.startswith('google-style-') or 'style' in sname or 'nasa' in sname:
        return 'style'
    if sname.startswith('sentry-') or 'sentry' in sname:
        return 'observability'
    if any(k in s for k in ['debug', 'triage', 'fix-defect', 'syncause', 'diagnose']):
        return 'debug'
    if any(k in s for k in ['security', 'phi', 'hipaa', 'auth', 'bounty', 'gateguard', 'taint', 'sec']):
        return 'security'
    if any(k in s for k in ['nextjs', 'react', 'supabase', 'tailwind', 'frontend', 'ui', 'vue', 'svelte', 'html']):
        return 'web'
    if any(k in s for k in ['python', 'typescript', 'swift', 'perl', 'java', 'go', 'node', 'cisco']):
        return 'lang'
    if any(k in s for k in ['docker', 'kubernetes', 'deploy', 'vercel', 'render', 'cloudflare', 'uncloud', 'ci-cd']):
        return 'devops'
    if any(k in s for k in ['postgres', 'mysql', 'redis', 'clickhouse', 'database', 'migration', 'sql']):
        return 'data'
    if any(k in s for k in ['agent', 'llm', 'mcp', 'prompt', 'eval', 'ai-first', 'autonomous']):
        return 'ai-ml'
    return 'workflow'


def infer_tags(sname: str, category: str, body: str) -> list[str]:
    tags = {category}
    tokens = re.findall(r'[a-zA-Z0-9]+', sname.lower())
    tags.update(t for t in tokens if len(t) > 2 and t not in {'and', 'the', 'for', 'with'})
    return sorted(list(tags))


def infer_dependencies(sname: str, body: str) -> list[str]:
    deps = []
    if 'systematic-debugging' in body and sname != 'systematic-debugging':
        deps.append('systematic-debugging')
    if 'tdd' in body and sname != 'tdd' and sname != 'tdd-workflow':
        deps.append('tdd-workflow')
    if 'verification-before-completion' in body and sname != 'verification-before-completion':
        deps.append('verification-before-completion')
    return sorted(list(set(deps)))


def estimate_tokens(body: str) -> int:
    return len(body) // 4


def build_index():
    print(f"Scanning skills in {SKILLS_DIR}...")
    skill_mds = sorted(list(SKILLS_DIR.rglob("SKILL.md")))
    skills_registry = {}
    namespaces_registry = {}
    aliases_registry = ALIAS_MAP.copy()

    for skill_md in skill_mds:
        skill_path = skill_md.parent
        dir_name = skill_path.name
        try:
            content = skill_md.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {skill_md}: {e}", file=sys.stderr)
            continue

        meta, body = strip_frontmatter(content)
        name = str(meta.get('name') or dir_name).strip()
        description = str(meta.get('description') or '').replace('\n', ' ').strip()
        category = str(meta.get('category') or infer_category(name, description, body)).strip()
        tags = meta.get('tags') if isinstance(meta.get('tags'), list) else infer_tags(name, category, body)
        dependencies = meta.get('dependencies') if isinstance(meta.get('dependencies'), list) else infer_dependencies(name, body)
        supported_tools = meta.get('supported_tools') if isinstance(meta.get('supported_tools'), list) else ["*"]
        version = str(meta.get('version') or "1.0.0").strip()
        last_updated = str(meta.get('last_updated') or "2026-07-27").strip()
        aliases = meta.get('aliases') if isinstance(meta.get('aliases'), list) else []

        # Short name for namespace
        short_name = name
        if name.startswith('gsd-'):
            short_name = name[4:]
        elif name.startswith('google-style-'):
            short_name = name[13:]
        elif name.startswith('sentry-'):
            short_name = name[7:]

        namespace_cmd = f"/{category}/{short_name}"
        flat_cmd = f"/{name}"

        rel_path = str(skill_md.relative_to(REPO_ROOT))

        skill_entry = {
            "name": name,
            "category": category,
            "category_label": CATEGORY_MAP.get(category, category.title()),
            "description": description,
            "namespace_command": namespace_cmd,
            "flat_command": flat_cmd,
            "aliases": sorted(list(set(aliases))),
            "tags": tags,
            "dependencies": dependencies,
            "supported_tools": supported_tools,
            "estimated_tokens": estimate_tokens(body),
            "version": version,
            "last_updated": last_updated,
            "rel_path": rel_path,
        }

        skills_registry[name] = skill_entry
        namespaces_registry[namespace_cmd] = name

    index_data = {
        "metadata": {
            "total_skills": len(skills_registry),
            "total_categories": len(CATEGORY_MAP),
            "generated_at": "2026-07-27T21:50:00Z",
            "schema_version": "2.0.0",
        },
        "categories": CATEGORY_MAP,
        "skills": skills_registry,
        "namespaces": namespaces_registry,
        "aliases": aliases_registry,
    }

    INDEX_FILE.write_text(json.dumps(index_data, indent=2), encoding='utf-8')
    print(f"Indexed {len(skills_registry)} skills into {INDEX_FILE}")


if __name__ == '__main__':
    build_index()
