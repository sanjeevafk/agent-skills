#!/usr/bin/env python3
"""
search_skills.py — Smart search and recommendation engine for skills and capabilities.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
COMMANDS_DIR = REPO_ROOT / 'commands'


def search(query: str, top_k: int = 10):
    if not INDEX_FILE.exists():
        print("skills.json not found. Run build_index.py first.")
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    skills = data['skills']
    query_tokens = [t.lower() for t in re.findall(r'\w+', query) if len(t) > 2]

    results = []
    for name, meta in skills.items():
        score = 0
        desc = meta['description'].lower()
        tags = [t.lower() for t in meta.get('tags', [])]
        category = meta.get('category', '').lower()

        for qt in query_tokens:
            if qt == name.lower():
                score += 100
            elif qt in name.lower():
                score += 30
            if qt in desc:
                score += 15
            if any(qt in t for t in tags):
                score += 20
            if qt in category:
                score += 10

        if score > 0:
            results.append((score, meta))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]


def generate_find_command():
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    find_cmd_file = COMMANDS_DIR / 'find.md'
    content = """<!-- AUTO-GENERATED SEARCH WRAPPER — DO NOT EDIT MANUALLY -->
---
description: "Search and discover skills by intent, tags, language, or framework"
namespace: "/find"
flat_command: "/find"
---

# Command: /find <keyword>

> **Usage**: Type `/find <keyword>` (e.g. `/find nextjs`, `/find debugging`, `/find security`) to search the 388+ registered skills and rules.

---

*(Executed via `gskills search <query>` or interactive discovery CLI.)*
"""
    find_cmd_file.write_text(content, encoding='utf-8')


def main():
    generate_find_command()
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n🔍 Search results for '{query}':\n")
        results = search(query)
        if not results:
            print("No matching skills found.")
            return
        for score, meta in results:
            print(f"  • {meta['name']:<35} (Score: {score:>3}) [{meta['namespace_command']}]")
            print(f"    {meta['description'][:90]}")
            print()
    else:
        print("Usage: gskills search <query>")


if __name__ == '__main__':
    main()
