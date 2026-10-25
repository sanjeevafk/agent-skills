#!/usr/bin/env python3
"""
eval_skill.py - 3-Arm Evaluation Harness for AI Agent Skills
Based on Sergii Makarevych's Eval Framework (2026) and poteto-mode eval playbook.

Arms:
  Arm A: Baseline (No skill)
  Arm B: Candidate Skill
  Arm C: Length Control (Unrelated text of exact identical character/token length)

Metrics:
  1. Adherence: Did the agent follow the specific extracted directives?
  2. Effect: Did the output improve on hidden benchmarks beyond length control?
"""

import os
import sys
import argparse
import json
import re
import random
import string
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add script directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_skill import lint_skill

# Unrelated filler corpora for Arm C (Length Control)
LOREM_CORPUS = (
    "The astrophysical dynamics of binary pulsars demonstrate relativistic frame dragging "
    "under extreme gravitational curvature. Observational data collected from radio interferometry "
    "arrays indicate periodic modulation consistent with post-Newtonian approximations. "
    "High-energy plasma ejections from magnetar flares exhibit non-thermal synchrotron emission "
    "profiles that correlate with crustal rupture events. Thermodynamics of accretion disks around "
    "intermediate-mass black holes reveal turbulent magneto-rotational instability driving angular "
    "momentum transport across event horizon boundaries."
)

def generate_length_control(target_length: int) -> str:
    """Generate unrelated text matching the exact character length of the skill."""
    words = LOREM_CORPUS.split()
    generated = []
    current_len = 0
    while current_len < target_length:
        w = random.choice(words)
        if current_len + len(w) + 1 <= target_length:
            generated.append(w)
            current_len += len(w) + 1
        else:
            padding = string.ascii_letters
            remainder = target_length - current_len
            if remainder > 0:
                generated.append("".join(random.choices(padding, k=remainder)))
            break
    return " ".join(generated)[:target_length]

def parse_skill(skill_path: Path) -> Dict:
    """Extract frontmatter, directives, and token/character length from SKILL.md."""
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill file not found at: {skill_path}")

    text = skill_path.read_text(encoding="utf-8")
    
    # Extract frontmatter
    name = skill_path.parent.name
    desc = ""
    fm_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
        desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()

    # Extract testable directives/points
    directives = []
    for line in text.splitlines():
        line_clean = line.strip()
        if re.match(r"^[-*]\s+\*\*.*?\*\*", line_clean) or re.match(r"^\d+\.\s+\*\*.*?\*\*", line_clean):
            directives.append(line_clean)
        elif line_clean.startswith("- ") or line_clean.startswith("* ") or re.match(r"^\d+\.\s+", line_clean):
            if len(line_clean) > 20 and not line_clean.startswith("#"):
                directives.append(line_clean)

    char_count = len(text)
    est_tokens = int(char_count / 4)

    return {
        "path": str(skill_path),
        "name": name,
        "description": desc,
        "raw_text": text,
        "char_count": char_count,
        "est_tokens": est_tokens,
        "directives": directives
    }

def scaffold_eval_workspace(skill_info: Dict, target_dir: Path, organic_prompt: str) -> Dict[str, Path]:
    """Scaffold blinded 3-arm test directories."""
    os.makedirs(target_dir, exist_ok=True)
    
    arm_dirs = {
        "arm_a_baseline": target_dir / "arm_a_baseline",
        "arm_b_candidate": target_dir / "arm_b_candidate",
        "arm_c_control": target_dir / "arm_c_control",
    }

    for name, p in arm_dirs.items():
        if p.exists():
            shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)
        # Store organic prompt
        (p / "PROMPT.txt").write_text(organic_prompt, encoding="utf-8")

    # Arm A: Empty skill injection
    (arm_dirs["arm_a_baseline"] / "SKILL_INJECTED.txt").write_text("", encoding="utf-8")

    # Arm B: Actual skill
    (arm_dirs["arm_b_candidate"] / "SKILL_INJECTED.txt").write_text(skill_info["raw_text"], encoding="utf-8")

    # Arm C: Length control text
    control_text = generate_length_control(skill_info["char_count"])
    (arm_dirs["arm_c_control"] / "SKILL_INJECTED.txt").write_text(control_text, encoding="utf-8")

    # Save manifest for judge
    manifest = {
        "skill_name": skill_info["name"],
        "char_count": skill_info["char_count"],
        "est_tokens": skill_info["est_tokens"],
        "directives_count": len(skill_info["directives"]),
        "directives": skill_info["directives"],
        "arms": {k: str(v) for k, v in arm_dirs.items()}
    }
    (target_dir / "eval_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return arm_dirs

def grade_and_decide(arm_a_score: float, arm_b_score: float, arm_c_score: float, adherence_rate: float) -> Tuple[str, str]:
    """
    Apply Makarevych's Dual-Metric Decision Matrix:
    - Low Adherence (<70%): Rewrite text
    - High Adherence + Flat Effect (B <= C): Drop idea
    - High Adherence + Genuine Lift (B > C > A): Ship & Pin
    """
    if adherence_rate < 0.70:
        verdict = "REWRITE TEXT"
        reason = f"Adherence is only {adherence_rate*100:.1f}%. The agent failed to reliably follow the skill directives."
    elif arm_b_score <= arm_c_score:
        verdict = "DROP IDEA (FOLKLORE)"
        reason = f"Skill effect ({arm_b_score:.2f}) did not beat length control ({arm_c_score:.2f}). Gains were placebo/length-driven."
    elif arm_b_score > arm_c_score and arm_b_score > arm_a_score:
        verdict = "SHIP & PIN"
        reason = f"Skill delivered genuine causal lift: Arm B ({arm_b_score:.2f}) > Arm C ({arm_c_score:.2f}) > Baseline ({arm_a_score:.2f})."
    else:
        verdict = "INCONCLUSIVE"
        reason = "Scores did not show statistically separable separation. Re-run with more trials."
        
    return verdict, reason

def print_scorecard(skill_info: Dict, results: Dict):
    print("\n" + "=" * 60)
    print(f"📊 EVALUATION SCORECARD: {skill_info['name']}")
    print("=" * 60)
    print(f"Skill Size:      {skill_info['char_count']} chars (~{skill_info['est_tokens']} tokens)")
    print(f"Directives:      {len(skill_info['directives'])} extracted test points")
    print("-" * 60)
    print("RESULTS BY ARM:")
    print(f"  Arm A (Baseline):       Score = {results['arm_a_score']:.2f}")
    print(f"  Arm B (Candidate):      Score = {results['arm_b_score']:.2f}  |  Adherence = {results['adherence_rate']*100:.1f}%")
    print(f"  Arm C (Length Control): Score = {results['arm_c_score']:.2f}")
    print("-" * 60)
    verdict, reason = grade_and_decide(
        results['arm_a_score'],
        results['arm_b_score'],
        results['arm_c_score'],
        results['adherence_rate']
    )
    print(f"VERDICT:  \033[1;32m{verdict}\033[0m" if verdict == "SHIP & PIN" else f"VERDICT:  \033[1;31m{verdict}\033[0m")
    print(f"ANALYSIS: {reason}")
    print("=" * 60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="3-Arm Skill Eval Harness")
    parser.add_argument("skill", help="Path to SKILL.md or skill name")
    parser.add_argument("--prompt", default="Implement a high-performance LRU cache in Python with O(1) ops and thread safety.", help="Organic test task prompt")
    parser.add_argument("--outdir", default="/tmp/skill_eval_workspace", help="Workspace for isolated trial sandboxes")
    parser.add_argument("--scaffold-only", action="store_true", help="Only scaffold the 3-arm sandboxes and manifest")
    parser.add_argument("--mock-run", action="store_true", help="Run simulated grading pipeline for dry-run verification")

    args = parser.parse_args()

    skill_path = Path(args.skill)
    if not skill_path.exists():
        # Check standard skill dirs
        candidates = [
            Path(os.path.expanduser("~/.gemini/config/skills")) / args.skill / "SKILL.md",
            Path(os.path.expanduser("~/.agents/skills")) / args.skill / "SKILL.md",
            Path(os.path.expanduser("~/Downloads/agent-skills/canonical")) / args.skill / "SKILL.md",
        ]
        found = False
        for c in candidates:
            if c.exists():
                skill_path = c
                found = True
                break
        if not found:
            print(f"Error: Could not locate skill '{args.skill}'", file=sys.stderr)
            sys.exit(1)

    # Stage 0: Pre-Eval Quality Gate (Makarevych Standard)
    passed, errors, warnings = lint_skill(skill_path)
    if not passed:
        print(f"\n❌ [Stage 0 Gate Failed] Cannot evaluate '{skill_path.parent.name}' due to quality errors:")
        for e in errors:
            print(f"   - {e}")
        print("\nResolve linting errors before spending compute on 3-arm evals.\n")
        sys.exit(1)

    skill_info = parse_skill(skill_path)
    outdir = Path(args.outdir)

    print(f"\n🔍 Parsing Skill: {skill_info['name']}")
    print(f"   Path:        {skill_info['path']}")
    print(f"   Footprint:   {skill_info['char_count']:,} chars (~{skill_info['est_tokens']:,} tokens)")
    print(f"   Directives:  {len(skill_info['directives'])} key points extracted")

    arm_dirs = scaffold_eval_workspace(skill_info, outdir, args.prompt)
    print(f"\n📁 Scaffolded 3-arm trial sandboxes in: {outdir}")
    print(f"   [Arm A] Baseline:       {arm_dirs['arm_a_baseline']}")
    print(f"   [Arm B] Candidate:      {arm_dirs['arm_b_candidate']}")
    print(f"   [Arm C] Length Control: {arm_dirs['arm_c_control']}")

    if args.scaffold_only:
        print("\nScaffolding complete. Manifest written to eval_manifest.json.")
        sys.exit(0)

    if args.mock_run:
        # Example validation run to verify harness logic
        results = {
            "arm_a_score": 0.65,
            "arm_b_score": 0.92,
            "arm_c_score": 0.68,
            "adherence_rate": 0.88
        }
        print_scorecard(skill_info, results)

if __name__ == "__main__":
    main()
