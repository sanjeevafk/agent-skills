#!/usr/bin/env bash
set -euo pipefail

# Global skill roots across your installed agent environments.
ROOT_COPILOT="${HOME}/.copilot/skills"
ROOT_AGENTS="${HOME}/.agents/skills"
ROOT_CURSOR="${HOME}/.cursor/skills"
ROOT_ANTIGRAVITY="${HOME}/.gemini/antigravity/skills"
ROOT_CODEX="${HOME}/.codex/skills"

CANONICAL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY")
ALL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_CODEX")

usage() {
  cat <<'EOF'
Usage:
  global-skills.sh backup [backup_dir]
  global-skills.sh add <owner/repo> [--skill <name> ...]
  global-skills.sh sync
  global-skills.sh status

Examples:
  global-skills.sh backup
  global-skills.sh add mattpocock/skills
  global-skills.sh add obra/superpowers --skill systematic-debugging
  global-skills.sh sync

What each command does:
  backup  Creates tar.gz backups for each global skill root + a manifest.
  add     Runs Skills CLI install globally, then syncs skills to all roots.
  sync    Copies all discovered SKILL.md-based skills to all roots.
  status  Prints skill counts per root and missing-in-codex summary.
EOF
}

ensure_roots() {
  local root
  for root in "${ALL_ROOTS[@]}"; do
    mkdir -p "$root"
  done
}

list_canonical_skills() {
  local root d
  for root in "${CANONICAL_ROOTS[@]}"; do
    [ -d "$root" ] || continue
    for d in "$root"/*; do
      [ -d "$d" ] || continue
      [ -f "$d/SKILL.md" ] || continue
      basename "$d"
    done
  done | sort -u
}

first_skill_source() {
  local skill="$1"
  local root
  for root in "${CANONICAL_ROOTS[@]}"; do
    if [ -f "$root/$skill/SKILL.md" ]; then
      printf '%s\n' "$root/$skill"
      return 0
    fi
  done
  return 1
}

sync_all() {
  ensure_roots

  local skill src dest_path dest_root src_real dst_real
  while IFS= read -r skill; do
    src="$(first_skill_source "$skill")"
    src_real="$(readlink -f "$src" || printf '%s' "$src")"

    for dest_root in "${ALL_ROOTS[@]}"; do
      dest_path="$dest_root/$skill"

      if [ -L "$dest_path" ] && [ ! -e "$dest_path" ]; then
        rm -f "$dest_path"
      fi
      if [ -e "$dest_path" ] && [ ! -d "$dest_path" ]; then
        rm -f "$dest_path"
      fi
      mkdir -p "$dest_path"

      dst_real="$(readlink -f "$dest_path" || printf '%s' "$dest_path")"
      if [ "$src_real" = "$dst_real" ]; then
        continue
      fi

      cp -a "$src/." "$dest_path/"
    done
  done < <(list_canonical_skills)

  printf 'Sync complete.\n'
}

backup_all() {
  ensure_roots

  local backup_dir
  if [ "${1:-}" != "" ]; then
    backup_dir="$1"
  else
    backup_dir="${HOME}/.skills/backups/skills-$(date +%Y%m%d-%H%M%S)"
  fi

  mkdir -p "$backup_dir"

  local root label count
  {
    echo "Global skills backup"
    echo "Created: $(date -Iseconds)"
    echo
  } > "$backup_dir/manifest.txt"

  for root in "${ALL_ROOTS[@]}"; do
    label="$(echo "$root" | sed 's#^/##; s#[^a-zA-Z0-9._-]#_#g')"
    tar -czf "$backup_dir/${label}.tar.gz" -C "$(dirname "$root")" "$(basename "$root")"
    count="$(find "$root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
    echo "$root -> $count entries" >> "$backup_dir/manifest.txt"
  done

  echo
  echo "Backup created at: $backup_dir"
  echo "Manifest: $backup_dir/manifest.txt"
}

status() {
  ensure_roots

  local root count
  for root in "${ALL_ROOTS[@]}"; do
    count="$(find "$root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
    echo "$root: $count entries"
  done

  local missing=0 skill
  while IFS= read -r skill; do
    if [ ! -f "$ROOT_CODEX/$skill/SKILL.md" ]; then
      missing=$((missing + 1))
    fi
  done < <(list_canonical_skills)

  echo "Missing SKILL.md entries in Codex vs canonical roots: $missing"
}

cmd="${1:-}"
case "$cmd" in
  backup)
    backup_all "${2:-}"
    ;;
  add)
    shift || true
    if [ "${1:-}" = "" ]; then
      echo "Error: add requires <owner/repo>"
      usage
      exit 1
    fi

    repo="$1"
    shift || true

    # Install through Skills CLI, then propagate for full cross-agent parity.
    CI=1 npx skills add "$repo" "$@" -g -y
    sync_all
    ;;
  sync)
    sync_all
    ;;
  status)
    status
    ;;
  *)
    usage
    exit 1
    ;;
esac
