#!/usr/bin/env python3
"""
compile_and_deploy.py — Compile agent skills with frontmatter preserved and deploy to all agent roots.

Usage:
  python3 scripts/compile_and_deploy.py
  python3 scripts/compile_and_deploy.py --dry-run
  python3 scripts/compile_and_deploy.py --skills-dir ./skills
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COMPILER = REPO_ROOT / "crates" / "skills-compiler" / "target" / "release" / "skills-compiler"
DEFAULT_SKILLS_DIR = REPO_ROOT / "skills"
CONFIG_FILE = Path(os.environ.get("GLOBAL_SKILLS_CONFIG", Path.home() / ".global-skills.conf"))


def parse_config(config_file: Path) -> dict:
    config = {}
    if not config_file.exists():
        return config
    for line in config_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip().strip("\"'")
    return config


def get_agent_roots(config: dict) -> list[Path]:
    default_roots = [
        config.get("ROOT_AGENTS", str(Path.home() / ".agents" / "skills")),
        config.get("ROOT_COPILOT", str(Path.home() / ".copilot" / "skills")),
        config.get("ROOT_CURSOR", str(Path.home() / ".cursor" / "skills")),
        config.get("ROOT_ANTIGRAVITY", str(Path.home() / ".gemini" / "skills")),
        config.get("ROOT_CODEX", str(Path.home() / ".codex" / "skills")),
        config.get("ROOT_HERMES", str(Path.home() / ".hermes" / "skills")),
        config.get("ROOT_OPENCODE", str(Path.home() / ".config" / "opencode" / "skills")),
        config.get("ROOT_CMD", str(Path.home() / ".commandcode" / "skills")),
    ]
    return [Path(r) for r in default_roots if r]


def compile_and_deploy(skills_dir: Path, compiler_bin: Path, dry_run: bool = False):
    if not compiler_bin.exists():
        print(f"Error: Compiler binary not found at {compiler_bin}", file=sys.stderr)
        print("Please build it first: cargo build --release --manifest-path crates/skills-compiler/Cargo.toml", file=sys.stderr)
        sys.exit(1)

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    skill_dirs.sort(key=lambda d: d.name)
    print(f"Found {len(skill_dirs)} skills to compile...")

    config = parse_config(CONFIG_FILE)
    roots = get_agent_roots(config)

    total_orig_chars = 0
    total_comp_chars = 0
    success_count = 0

    staging_dir = Path("/tmp/compiled_skills_staging")
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    for d in skill_dirs:
        skill_name = d.name
        src_skill_md = d / "SKILL.md"
        dest_dir = staging_dir / skill_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy non-SKILL.md assets (scripts, references, schemas, tests)
        for item in d.iterdir():
            if item.name == "SKILL.md":
                continue
            if item.is_dir():
                shutil.copytree(item, dest_dir / item.name, symlinks=True, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest_dir / item.name)

        orig_content = src_skill_md.read_text(encoding="utf-8", errors="replace")
        total_orig_chars += len(orig_content)

        # Compile using native Rust compiler with --keep-frontmatter
        try:
            res = subprocess.run(
                [str(compiler_bin), "compile", "--keep-frontmatter", "--input", str(src_skill_md)],
                capture_output=True,
                text=True,
                check=True
            )
            compiled_content = res.stdout
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to compile {skill_name}, using original: {e.stderr.strip()}", file=sys.stderr)
            compiled_content = orig_content

        total_comp_chars += len(compiled_content)
        (dest_dir / "SKILL.md").write_text(compiled_content, encoding="utf-8")
        success_count += 1

    pct_reduction = ((total_orig_chars - total_comp_chars) / total_orig_chars) * 100 if total_orig_chars > 0 else 0
    print(f"Compiled {success_count} skills: {total_orig_chars:,} -> {total_comp_chars:,} chars ({pct_reduction:.1f}% reduction)")

    if dry_run:
        print("[DRY-RUN] Skipping deployment to roots.")
        shutil.rmtree(staging_dir)
        return

    for root in roots:
        root.mkdir(parents=True, exist_ok=True)
        print(f"Deploying to {root}...")
        for skill_dir in staging_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            dest_skill_dir = root / skill_dir.name
            dest_skill_dir.mkdir(parents=True, exist_ok=True)
            for item in skill_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, dest_skill_dir / item.name, symlinks=True, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest_skill_dir / item.name)

    # Sync pi symlinks if pi environment exists
    pi_skills_dir = Path.home() / ".pi" / "agent" / "skills"
    if pi_skills_dir.exists():
        print(f"Updating pi symlinks in {pi_skills_dir}...")
        agents_root = Path(config.get("ROOT_AGENTS", str(Path.home() / ".agents" / "skills")))
        for skill_dir in staging_dir.iterdir():
            symlink_target = pi_skills_dir / skill_dir.name
            rel_target = Path(os.path.relpath(agents_root / skill_dir.name, pi_skills_dir))
            if not symlink_target.exists():
                try:
                    symlink_target.symlink_to(rel_target)
                except Exception as e:
                    print(f"Notice: could not create symlink for {skill_dir.name}: {e}", file=sys.stderr)

    shutil.rmtree(staging_dir)
    print("All skills successfully compiled and deployed across all agent environments!")


def main():
    parser = argparse.ArgumentParser(description="Compile skills preserving frontmatter and deploy to all agent environments.")
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_SKILLS_DIR, help="Path to skills directory")
    parser.add_argument("--compiler", type=Path, default=DEFAULT_COMPILER, help="Path to skills-compiler binary")
    parser.add_argument("--dry-run", action="store_true", help="Compile to verify without deploying")
    args = parser.parse_args()

    compile_and_deploy(args.skills_dir, args.compiler, args.dry_run)


if __name__ == "__main__":
    main()
