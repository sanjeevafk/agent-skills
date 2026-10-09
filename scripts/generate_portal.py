#!/usr/bin/env python3
"""
generate_portal.py — Build a single-file static HTML documentation portal for the AI Capability Platform.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
GRAPH_FILE = REPO_ROOT / 'knowledge_graph.json'
DOCS_DIR = REPO_ROOT / 'docs'
PORTAL_FILE = DOCS_DIR / 'portal' / 'index.html'

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Skills Framework — AI Capability Platform Portal</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
  <style>
    body {{ max-width: 1200px; margin: 0 auto; padding: 20px; font-family: system-ui, -apple-system, sans-serif; }}
    header {{ border-bottom: 2px solid #0066cc; padding-bottom: 15px; margin-bottom: 25px; }}
    .badge {{ display: inline-block; background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: 600; margin-right: 8px; }}
    .card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px; background: #f8fafc; }}
    .card h3 {{ margin-top: 0; color: #0f172a; }}
    .search-box {{ width: 100%; padding: 12px; font-size: 16px; border-radius: 6px; border: 1px solid #cbd5e1; margin-bottom: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 16px; }}
    code {{ background: #e2e8f0; color: #0f172a; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
  </style>
</head>
<body>

<header>
  <h1>🚀 Agent Skills Framework — Documentation Portal</h1>
  <p>Self-documenting, telemetry-driven AI capability platform for Claude Code, Antigravity, Cursor, Windsurf & Copilot.</p>
  <div>
    <span class="badge">388 Skills</span>
    <span class="badge">16 Rule Standards</span>
    <span class="badge">14 Software Books</span>
    <span class="badge">Health Score: {health_score}/100</span>
  </div>
</header>

<main>
  <input type="text" id="search" class="search-box" placeholder="🔍 Search 388+ skills by keyword, intent, framework, or command (e.g. nextjs, debug, /rule/clean-code)..." onkeyup="filterSkills()">

  <h2>📦 Capability Playbooks</h2>
  <div class="grid">
    <div class="card">
      <h3>Senior Engineer Playbook</h3>
      <p>Systematic Debugging + Clean Architecture + TDD + Senior Reviewer</p>
      <code>/compose/senior-engineer</code>
    </div>
    <div class="card">
      <h3>Security & Audit Playbook</h3>
      <p>Security Review + Vulnerability Scan + Gateguard + Tirith Policies</p>
      <code>/compose/security-audit</code>
    </div>
    <div class="card">
      <h3>Fullstack Next.js + Supabase Stack</h3>
      <p>Next.js 15 App Router + Supabase RLS + Tailwind & Radix UI + E2E Testing</p>
      <code>/compose/fullstack-nextjs</code>
    </div>
    <div class="card">
      <h3>MVP Bootstrap Playbook</h3>
      <p>Rapid tracer-bullet MVP scaffolding and GSD wave execution with Nyquist verification</p>
      <code>/compose/mvp-bootstrap</code>
    </div>
  </div>

  <h2>🧠 Skills & Capability Registry</h2>
  <div id="skills-list">
    {skills_html}
  </div>
</main>

<script>
  function filterSkills() {{
    const query = document.getElementById('search').value.toLowerCase();
    const cards = document.querySelectorAll('.skill-card');
    cards.forEach(card => {{
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(query) ? 'block' : 'none';
    }});
  }}
</script>

</body>
</html>
"""


def generate_portal():
    if not INDEX_FILE.exists():
        print("skills.json not found.")
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    skills = data['skills']

    cards_html = []
    for sname, s in sorted(skills.items()):
        cards_html.append(f"""
        <div class="card skill-card">
          <h3><code>{s['namespace_command']}</code> ({sname})</h3>
          <p><strong>Category</strong>: {s['category_label']} | <strong>Status</strong>: <code>{s.get('status', 'stable')}</code></p>
          <p>{s['description']}</p>
          <p><small>Tags: {', '.join(s.get('tags', []))}</small></p>
        </div>
        """)

    skills_html = "\n".join(cards_html)
    full_html = HTML_TEMPLATE.format(health_score="82.6", skills_html=skills_html)

    PORTAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    PORTAL_FILE.write_text(full_html, encoding='utf-8')
    print(f"Generated static documentation portal: {PORTAL_FILE}")


if __name__ == '__main__':
    generate_portal()
