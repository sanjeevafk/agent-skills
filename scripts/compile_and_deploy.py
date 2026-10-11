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
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COMPILER = REPO_ROOT / "crates" / "skills-compiler" / "target" / "release" / "skills-compiler"
DEFAULT_SKILLS_DIR = REPO_ROOT / "skills"
CONFIG_FILE = Path(os.path.expandvars(os.path.expanduser(os.environ.get("GLOBAL_SKILLS_CONFIG", "~/.global-skills.conf")))).resolve()


def parse_config(config_file: Path) -> dict:
    config = {}
    if not config_file.exists():
        return config
    for line in config_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        # Drop inline comments and empty lines
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        # Strip optional shell 'export ' prefix
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("\"'")
            config[k] = v
    return config


def get_agent_roots(config: dict) -> list[Path]:
    default_roots = [
        config.get("ROOT_AGENTS", "~/.agents/skills"),
        config.get("ROOT_COPILOT", "~/.copilot/skills"),
        config.get("ROOT_CURSOR", "~/.cursor/skills"),
        config.get("ROOT_ANTIGRAVITY", "~/.gemini/skills"),
        config.get("ROOT_CODEX", "~/.codex/skills"),
        config.get("ROOT_HERMES", "~/.hermes/skills"),
        config.get("ROOT_OPENCODE", "~/.config/opencode/skills"),
        config.get("ROOT_CMD", "~/.commandcode/skills"),
    ]
    roots = []
    for r in default_roots:
        if not r:
            continue
        expanded = Path(os.path.expandvars(os.path.expanduser(r))).resolve()
        roots.append(expanded)
    return roots


def safe_copy_assets(src_dir: Path, dest_dir: Path):
    """Recursively copy non-SKILL.md assets with strict containment checks to prevent symlink traversal."""
    resolved_src = src_dir.resolve()
    for root, dirs, files in os.walk(src_dir, followlinks=False):
        rel_root = Path(root).relative_to(src_dir)
        target_root = dest_dir / rel_root
        target_root.mkdir(parents=True, exist_ok=True)

        # Filter directories to avoid recursing into out-of-tree symlinked dirs
        safe_dirs = []
        for d in dirs:
            d_path = Path(root) / d
            if d_path.is_symlink():
                try:
                    resolved_d = d_path.resolve(strict=False)
                    if not resolved_d.is_relative_to(resolved_src):
                        print(f"Warning: Skipping out-of-tree symlink directory {d_path}", file=sys.stderr)
                        continue
                except (ValueError, RuntimeError) as e:
                    print(f"Warning: Skipping unresolvable directory symlink {d_path}: {e}", file=sys.stderr)
                    continue
            safe_dirs.append(d)
        dirs[:] = safe_dirs

        for f in files:
            if rel_root == Path(".") and f == "SKILL.md":
                continue
            f_path = Path(root) / f
            if f_path.is_symlink():
                try:
                    resolved_f = f_path.resolve(strict=False)
                    if not resolved_f.is_relative_to(resolved_src):
                        print(f"Warning: Skipping out-of-tree file symlink {f_path}", file=sys.stderr)
                        continue
                except (ValueError, RuntimeError) as e:
                    print(f"Warning: Skipping unresolvable file symlink {f_path}: {e}", file=sys.stderr)
                    continue

            target_file = target_root / f
            shutil.copy2(f_path, target_file, follow_symlinks=False)


def clean_destination(dest_dir: Path):
    """Safely remove a destination skill directory, handling symlinks and real directories."""
    if dest_dir.is_symlink() or os.path.lexists(dest_dir):
        try:
            dest_dir.unlink()
        except OSError:
            shutil.rmtree(dest_dir, ignore_errors=True)
    elif dest_dir.is_dir():
        shutil.rmtree(dest_dir)


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
    compiled_count = 0
    fallback_count = 0

    with tempfile.TemporaryDirectory(prefix="compiled_skills_") as tmp_dir:
        staging_dir = Path(tmp_dir)

        for d in skill_dirs:
            skill_name = d.name
            src_skill_md = d / "SKILL.md"
            dest_dir = staging_dir / skill_name
            dest_dir.mkdir(parents=True, exist_ok=True)

            safe_copy_assets(d, dest_dir)

            orig_content = src_skill_md.read_text(encoding="utf-8", errors="replace")
            total_orig_chars += len(orig_content)

            try:
                res = subprocess.run(
                    [str(compiler_bin), "compile", "--keep-frontmatter", "--input", str(src_skill_md)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=True
                )
                compiled_content = res.stdout
                compiled_count += 1
            except subprocess.TimeoutExpired:
                print(f"Warning: Compilation timed out for {skill_name}, using original", file=sys.stderr)
                compiled_content = orig_content
                fallback_count += 1
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to compile {skill_name}, using original: {e.stderr.strip()}", file=sys.stderr)
                compiled_content = orig_content
                fallback_count += 1

            total_comp_chars += len(compiled_content)
            (dest_dir / "SKILL.md").write_text(compiled_content, encoding="utf-8")

        pct_reduction = ((total_orig_chars - total_comp_chars) / total_orig_chars) * 100 if total_orig_chars > 0 else 0
        print(f"Compilation summary: {compiled_count} compiled, {fallback_count} fallback")
        print(f"Character footprint: {total_orig_chars:,} -> {total_comp_chars:,} chars ({pct_reduction:.1f}% reduction)")

        if dry_run:
            print("[DRY-RUN] Skipping deployment to roots.")
            return

        for root in roots:
            root.mkdir(parents=True, exist_ok=True)
            print(f"Deploying to {root}...")
            for skill_dir in staging_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                dest_skill_dir = root / skill_dir.name
                clean_destination(dest_skill_dir)
                dest_skill_dir.mkdir(parents=True, exist_ok=True)

                for root_sub, _, files_sub in os.walk(skill_dir, followlinks=False):
                    rel_sub = Path(root_sub).relative_to(skill_dir)
                    target_sub = dest_skill_dir / rel_sub
                    target_sub.mkdir(parents=True, exist_ok=True)
                    for f in files_sub:
                        src_f = Path(root_sub) / f
                        dst_f = target_sub / f
                        shutil.copy2(src_f, dst_f, follow_symlinks=False)

        # Sync pi symlinks safely (handling stale or broken symlinks and cleaning orphans)
        pi_skills_dir = (Path.home() / ".pi" / "agent" / "skills").resolve()
        if pi_skills_dir.exists():
            print(f"Updating pi symlinks in {pi_skills_dir}...")
            agents_root = Path(os.path.expandvars(os.path.expanduser(config.get("ROOT_AGENTS", "~/.agents/skills")))).resolve()

            # Clean orphaned symlinks pointing to non-existent skills
            for item in pi_skills_dir.iterdir():
                if item.is_symlink():
                    try:
                        resolved_item = item.resolve()
                        if resolved_item.is_relative_to(agents_root) and not (staging_dir / item.name).exists():
                            print(f"Removing orphaned Pi symlink: {item.name}")
                            item.unlink()
                    except Exception:
                        if not os.path.lexists(item):
                            item.unlink()

            for skill_dir in staging_dir.iterdir():
                symlink_target = pi_skills_dir / skill_dir.name
                rel_target = Path(os.path.relpath(agents_root / skill_dir.name, pi_skills_dir))
                if symlink_target.is_symlink() or os.path.lexists(symlink_target):
                    try:
                        if symlink_target.resolve() == (agents_root / skill_dir.name).resolve():
                            continue
                        symlink_target.unlink()
                    except Exception:
                        pass
                try:
                    symlink_target.symlink_to(rel_target)
                except Exception as e:
                    print(f"Notice: could not create symlink for {skill_dir.name}: {e}", file=sys.stderr)

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
