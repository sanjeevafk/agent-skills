#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="${GLOBAL_SKILLS_CONFIG:-$HOME/.global-skills.conf}"

# Defaults (used if config file is missing)
DEFAULT_ROOT_AGENTS="${HOME}/.agents/skills"
DEFAULT_ROOT_COPILOT="${HOME}/.copilot/skills"
DEFAULT_ROOT_CURSOR="${HOME}/.cursor/skills"
DEFAULT_ROOT_ANTIGRAVITY="${HOME}/.gemini/antigravity/skills"
DEFAULT_ROOT_CODEX="${HOME}/.codex/skills"
DEFAULT_BACKUP_BASE_DIR="${HOME}/.skills/backups"

ROOT_AGENTS="$DEFAULT_ROOT_AGENTS"
ROOT_COPILOT="$DEFAULT_ROOT_COPILOT"
ROOT_CURSOR="$DEFAULT_ROOT_CURSOR"
ROOT_ANTIGRAVITY="$DEFAULT_ROOT_ANTIGRAVITY"
ROOT_CODEX="$DEFAULT_ROOT_CODEX"
BACKUP_BASE_DIR="$DEFAULT_BACKUP_BASE_DIR"

# Arrays are rebuilt after optional config load.
CANONICAL_ROOTS=()
ALL_ROOTS=()

load_config() {
  if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
  fi

  CANONICAL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY")
  ALL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_CODEX")
}

write_default_config() {
  if [ -f "$CONFIG_FILE" ]; then
    echo "Config already exists: $CONFIG_FILE"
    return 0
  fi

  cat > "$CONFIG_FILE" <<CFG_EOF
# global-skills configuration
# Edit these paths to match your installed agent environments.

ROOT_AGENTS="${DEFAULT_ROOT_AGENTS}"
ROOT_COPILOT="${DEFAULT_ROOT_COPILOT}"
ROOT_CURSOR="${DEFAULT_ROOT_CURSOR}"
ROOT_ANTIGRAVITY="${DEFAULT_ROOT_ANTIGRAVITY}"
ROOT_CODEX="${DEFAULT_ROOT_CODEX}"

# Backup base directory used by: global-skills backup
BACKUP_BASE_DIR="${DEFAULT_BACKUP_BASE_DIR}"
CFG_EOF

  echo "Created default config: $CONFIG_FILE"
}

usage() {
  cat <<USAGE_EOF
Usage:
  global-skills backup [backup_dir]
  global-skills add <owner/repo> [--skill <name> ...]
  global-skills sync
  global-skills status
  global-skills init-config
  global-skills export [--format agentrules|cursor|copilot|windsurf|all] [--include skill1,skill2] [--output-dir DIR]
  global-skills import [skills_dir]

Config:
  Uses: $CONFIG_FILE
  Override file path with: GLOBAL_SKILLS_CONFIG=/path/to/file

Examples:
  global-skills init-config
  global-skills backup
  global-skills add mattpocock/skills
  global-skills add obra/superpowers --skill systematic-debugging
  global-skills sync
  global-skills export --format all
  global-skills export --format agentrules --output-dir ~/my-project
  global-skills export --format cursor --include google-style-python,google-style-typescript
  global-skills export --format copilot --output-dir ~/my-project
  global-skills import ./skills

What each command does:
  backup       Creates tar.gz backups for each global skill root + a manifest.
  add          Runs Skills CLI install globally, then syncs skills to all roots.
  sync         Copies all discovered SKILL.md-based skills to all roots.
  status       Prints skill counts per root and missing-in-codex summary.
  init-config  Creates $CONFIG_FILE with editable default root paths.
  export       Compile skills into .agentrules, .cursorrules, copilot-instructions.md, or .windsurfrules.
  import       Import local skills from a directory (defaults to ./skills) and sync them.
USAGE_EOF
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
    backup_dir="${BACKUP_BASE_DIR}/skills-$(date +%Y%m%d-%H%M%S)"
  fi

  mkdir -p "$backup_dir"

  local root label count
  {
    echo "Global skills backup"
    echo "Created: $(date -Iseconds)"
    echo "Config: $CONFIG_FILE"
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
  echo "Using config: $CONFIG_FILE"
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

load_config

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
  init-config)
    write_default_config
    ;;
  import)
    shift || true
    
    # Locate import source
    SRC_DIR="${1:-}"
    if [ -z "$SRC_DIR" ]; then
      # If run from within repository root, default to ./skills
      if [ -d "./skills" ]; then
        SRC_DIR="./skills"
      else
        # Fallback to look relative to this script's parent directory
        SCRIPT_PARENT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        if [ -d "$SCRIPT_PARENT/skills" ]; then
          SRC_DIR="$SCRIPT_PARENT/skills"
        fi
      fi
    fi

    if [ -z "$SRC_DIR" ] || [ ! -d "$SRC_DIR" ]; then
      echo "Error: Directory not found. Please specify local skills directory."
      exit 1
    fi

    # Destination is the first canonical root
    DEST_ROOT=""
    for r in "${CANONICAL_ROOTS[@]}"; do
      if [ -n "$r" ]; then
        DEST_ROOT="$r"
        break
      fi
    done

    if [ -z "$DEST_ROOT" ]; then
      echo "Error: No canonical roots defined in configuration."
      exit 1
    fi

    echo "Importing skills from $SRC_DIR to $DEST_ROOT..."
    mkdir -p "$DEST_ROOT"

    count=0
    for d in "$SRC_DIR"/*; do
      [ -d "$d" ] || continue
      [ -f "$d/SKILL.md" ] || continue
      sname="$(basename "$d")"
      echo "  -> Importing $sname"
      rm -rf "$DEST_ROOT/$sname"
      mkdir -p "$DEST_ROOT/$sname"
      cp -a "$d/." "$DEST_ROOT/$sname/"
      count=$((count + 1))
    done

    echo "Import complete ($count skills imported)."
    echo "Syncing imported skills across all environments..."
    sync_all
    ;;
  export)
    shift || true
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    EXPORT_SCRIPT="$SCRIPT_DIR/export_skills.py"
    if [ ! -f "$EXPORT_SCRIPT" ]; then
      echo "Error: export_skills.py not found at $EXPORT_SCRIPT"
      exit 1
    fi

    # Check if --skills-dir is explicitly passed
    local has_skills_dir=0
    for arg in "$@"; do
      if [[ "$arg" == "--skills-dir"* ]]; then
        has_skills_dir=1
      fi
    done

    if [ "$has_skills_dir" -eq 1 ]; then
      python3 "$EXPORT_SCRIPT" "$@"
    else
      # Default: find the first active canonical root with actual skills
      SKILLS_SOURCE=""
      for root in "${CANONICAL_ROOTS[@]}"; do
        if [ -d "$root" ] && [ -n "$(find "$root" -name SKILL.md 2>/dev/null)" ]; then
          SKILLS_SOURCE="$root"
          break
        fi
      done

      if [ -n "$SKILLS_SOURCE" ]; then
        python3 "$EXPORT_SCRIPT" --skills-dir "${SKILLS_SOURCE}" "$@"
      else
        python3 "$EXPORT_SCRIPT" "$@"
      fi
    fi
    ;;
  *)
    usage
    exit 1
    ;;
esac
