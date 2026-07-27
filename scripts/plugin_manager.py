#!/usr/bin/env python3
"""
plugin_manager.py — Manage, install, and update external capability plugins/packs.
"""

import json
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
SKILLS_DIR = REPO_ROOT / 'skills'
INDEX_FILE = REPO_ROOT / 'skills.json'


def install_plugin(repo: str, skill_name: str = None):
    print(f"📦 Installing capability plugin from '{repo}'...")

    cmd = ["npx", "-y", "skills", "add", repo, "-g", "-y"]
    if skill_name:
        cmd.extend(["--skill", skill_name])

    try:
        subprocess.run(cmd, check=True)
        print("✅ Plugin downloaded via Skills CLI. Re-indexing & building framework...")
        subprocess.run([sys.executable, str(REPO_ROOT / 'scripts' / 'build_index.py')], check=True)
        subprocess.run([sys.executable, str(REPO_ROOT / 'scripts' / 'generate_commands.py')], check=True)
        print(f"✅ Installed plugin package '{repo}'. Framework rebuilt!")
    except Exception as e:
        print(f"❌ Plugin installation failed: {e}", file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        repo = sys.argv[1]
        sk = sys.argv[2] if len(sys.argv) > 2 else None
        install_plugin(repo, sk)
    else:
        print("Usage: python3 plugin_manager.py <owner/repo> [skill_name]")
