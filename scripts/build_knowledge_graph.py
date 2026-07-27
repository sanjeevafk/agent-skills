#!/usr/bin/env python3
"""
build_knowledge_graph.py — Build a graph linking Skills, Rules, Agents, Commands, Hooks, Books, Frameworks, Languages, and Domains.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
GRAPH_FILE = REPO_ROOT / 'knowledge_graph.json'


def build_knowledge_graph():
    if not INDEX_FILE.exists():
        print("skills.json not found. Run build_index.py first.")
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    skills = data['skills']
    categories = data['categories']

    nodes = []
    links = []
    node_set = set()

    def add_node(nid, label, group):
        if nid not in node_set:
            nodes.append({"id": nid, "label": label, "group": group})
            node_set.add(nid)

    def add_link(source, target, relation):
        links.append({"source": source, "target": target, "relation": relation})

    # 1. Add Category & Rule Book nodes
    for cat_id, cat_label in categories.items():
        add_node(f"cat:{cat_id}", cat_label, "Category")

    books = [
        "clean-code", "clean-architecture", "refactoring", "the-pragmatic-programmer",
        "designing-data-intensive-applications", "a-philosophy-of-software-design",
        "domain-driven-design", "code-complete", "working-effectively-with-legacy-code", "release-it"
    ]
    for b in books:
        add_node(f"book:{b}", f"Book: {b.replace('-', ' ').title()}", "Book")

    # 2. Add Skills, Commands, and Links
    for sname, s in skills.items():
        add_node(f"skill:{sname}", sname, "Skill")

        # Link skill to category
        add_link(f"skill:{sname}", f"cat:{s['category']}", "belongs_to_category")

        # Link skill to command
        add_node(f"cmd:{sname}", s['flat_command'], "Command")
        add_link(f"skill:{sname}", f"cmd:{sname}", "exposes_command")

        # Link dependencies
        for dep in s.get('dependencies', []):
            add_node(f"skill:{dep}", dep, "Skill")
            add_link(f"skill:{sname}", f"skill:{dep}", "depends_on")

        # Link to books where relevant
        body_lower = str(s).lower()
        for b in books:
            if b.replace('-', ' ') in body_lower or b in body_lower:
                add_link(f"skill:{sname}", f"book:{b}", "governed_by_book")

    graph_data = {
        "stats": {
            "total_nodes": len(nodes),
            "total_links": len(links),
        },
        "nodes": nodes,
        "links": links,
    }

    GRAPH_FILE.write_text(json.dumps(graph_data, indent=2), encoding='utf-8')
    print(f"Generated Knowledge Graph: {GRAPH_FILE} ({len(nodes)} nodes, {len(links)} semantic edges)")


if __name__ == '__main__':
    build_knowledge_graph()
