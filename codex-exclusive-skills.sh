#!/usr/bin/env bash
set -euo pipefail

# Manage Codex-exclusive skills (not synced to canonical roots by default).
# These skills exist ONLY in ~/.codex/skills and can be selectively propagated to other agents.

# Canonical roots (where we can push Codex skills if needed)
ROOT_AGENTS="${HOME}/.agents/skills"
ROOT_COPILOT="${HOME}/.copilot/skills"
ROOT_CURSOR="${HOME}/.cursor/skills"
ROOT_ANTIGRAVITY="${HOME}/.gemini/antigravity/skills"
ROOT_CODEX="${HOME}/.codex/skills"

CANONICAL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY")
ALL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_CODEX")

usage() {
  cat <<'EOF'
Usage:
  codex-exclusive-skills.sh list
  codex-exclusive-skills.sh propagate [--skill <name> ...]
  codex-exclusive-skills.sh remove-from-codex <name> ...
  codex-exclusive-skills.sh compare

Examples:
  codex-exclusive-skills.sh list
  codex-exclusive-skills.sh propagate
  codex-exclusive-skills.sh propagate --skill cloudflare-deploy --skill vercel-deploy
  codex-exclusive-skills.sh remove-from-codex yeet
  codex-exclusive-skills.sh compare

What each command does:
  list           Show all Codex-only skills with descriptions.
  propagate      Copy selected or all Codex-only skills to canonical roots.
  remove-from-codex
                 Delete skills from ~/.codex/skills.
  compare        Show skill differences between Codex and canonical roots.
EOF
}

# List all skills in Codex that don't exist in any canonical root
list_codex_exclusive() {
  local skill
  for skill in "$ROOT_CODEX"/*; do
    [ -d "$skill" ] || continue
    [ -f "$skill/SKILL.md" ] || continue
    skill_name=$(basename "$skill")
    
    # Check if it exists in ANY canonical root
    local found=0
    for croot in "${CANONICAL_ROOTS[@]}"; do
      if [ -f "$croot/$skill_name/SKILL.md" ]; then
        found=1
        break
      fi
    done
    
    if [ $found -eq 0 ]; then
      printf '%s\n' "$skill_name"
    fi
  done
}

# Show Codex-exclusive skills  with pointers to documentation
show_descriptions() {
  echo "Codex-Exclusive Skills (14 total)"
  echo ""
  list_codex_exclusive | nl
  echo ""
  echo "For details on each skill, see docs/CODEX_EXCLUSIVE_SKILLS.md or run:"
  echo "  ~/Downloads/agent-skills/codex-exclusive-skills.sh compare"
}

# Propagate Codex skills to canonical roots
propagate_to_canonical() {
  local specified_skills=()
  local all_skills=false
  
  # Parse arguments
  while [ $# -gt 0 ]; do
    case "$1" in
      --skill)
        shift
        specified_skills+=("$1")
        shift
        ;;
      *)
        shift
        ;;
    esac
  done
  
  # If no skills specified, use all
  if [ ${#specified_skills[@]} -eq 0 ]; then
    all_skills=true
  fi
  
  local skill
  while IFS= read -r skill; do
    # Skip if skills were specified and this one isn't in the list
    if [ "$all_skills" = false ]; then
      local found=0
      for specified in "${specified_skills[@]}"; do
        if [ "$specified" = "$skill" ]; then
          found=1
          break
        fi
      done
      [ $found -eq 1 ] || continue
    fi
    
    local src="$ROOT_CODEX/$skill"
    printf 'Propagating: %s\n' "$skill"
    
    for dest_root in "${CANONICAL_ROOTS[@]}"; do
      mkdir -p "$dest_root/$skill"
      cp -a "$src/." "$dest_root/$skill/"
    done
  done < <(list_codex_exclusive)
  
  printf '\nPropagation complete.\n'
}

# Remove skills from Codex
remove_from_codex() {
  for skill in "$@"; do
    local skillpath="$ROOT_CODEX/$skill"
    
    if [ ! -d "$skillpath" ]; then
      printf 'Skill not found: %s\n' "$skill"
      continue
    fi
    
    printf 'Removing from Codex: %s\n' "$skill"
    rm -rf "$skillpath"
  done
  
  printf 'Removal complete.\n'
}

# Compare Codex vs Canonical for all skills
compare_roots() {
  echo "=== Codex vs Canonical Roots ===" 
  echo ""
  echo "Skills ONLY in Codex (exclusive):"
  list_codex_exclusive | nl
  
  echo ""
  echo "Skills in BOTH:"
  local both=0
  for skill in "$ROOT_CODEX"/*; do
    [ -d "$skill" ] || continue
    [ -f "$skill/SKILL.md" ] || continue
    skill_name=$(basename "$skill")
    
    for croot in "${CANONICAL_ROOTS[@]}"; do
      if [ -f "$croot/$skill_name/SKILL.md" ]; then
        printf '%s\n' "$skill_name"
        both=$((both + 1))
        break
      fi
    done
  done | sort -u | nl
  
  echo ""
  echo "Summary:"
  echo "  Codex total: $(find "$ROOT_CODEX" -maxdepth 1 -type d -not -name '.*' | wc -l)"
  echo "  Exclusive: $(list_codex_exclusive | wc -l)"
  echo "  Shared: $both"
}

cmd="${1:-}"
case "$cmd" in
  list)
    show_descriptions
    ;;
  propagate)
    shift
    propagate_to_canonical "$@"
    ;;
  remove-from-codex)
    shift
    remove_from_codex "$@"
    ;;
  compare)
    compare_roots
    ;;
  *)
    usage
    exit 1
    ;;
esac
