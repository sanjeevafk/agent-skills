#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="${GLOBAL_SKILLS_CONFIG:-$HOME/.global-skills.conf}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Defaults (used if config file is missing)
DEFAULT_ROOT_AGENTS="${HOME}/.agents/skills"
DEFAULT_ROOT_COPILOT="${HOME}/.copilot/skills"
DEFAULT_ROOT_CURSOR="${HOME}/.cursor/skills"
DEFAULT_ROOT_ANTIGRAVITY="${HOME}/.gemini/antigravity/skills"
DEFAULT_ROOT_CODEX="${HOME}/.codex/skills"
DEFAULT_ROOT_HERMES="${HOME}/.hermes/skills"
DEFAULT_ROOT_OPENCODE="${HOME}/.config/opencode/skills"
DEFAULT_ROOT_CMD="${HOME}/.commandcode/skills"
DEFAULT_BACKUP_BASE_DIR="${HOME}/.skills/backups"

ROOT_AGENTS="$DEFAULT_ROOT_AGENTS"
ROOT_COPILOT="$DEFAULT_ROOT_COPILOT"
ROOT_CURSOR="$DEFAULT_ROOT_CURSOR"
ROOT_ANTIGRAVITY="$DEFAULT_ROOT_ANTIGRAVITY"
ROOT_CODEX="$DEFAULT_ROOT_CODEX"
ROOT_HERMES="$DEFAULT_ROOT_HERMES"
ROOT_OPENCODE="$DEFAULT_ROOT_OPENCODE"
ROOT_CMD="$DEFAULT_ROOT_CMD"
BACKUP_BASE_DIR="$DEFAULT_BACKUP_BASE_DIR"

# Arrays are rebuilt after optional config load.
CANONICAL_ROOTS=()
ALL_ROOTS=()

load_config() {
  if [ -f "$CONFIG_FILE" ]; then
    # Parse only the documented KEY=value format; never execute config contents.
    while IFS= read -r line || [ -n "$line" ]; do
      [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
      if [[ "$line" =~ ^[[:space:]]*(ROOT_AGENTS|ROOT_COPILOT|ROOT_CURSOR|ROOT_ANTIGRAVITY|ROOT_CODEX|ROOT_HERMES|ROOT_OPENCODE|ROOT_CMD|BACKUP_BASE_DIR|REPO_DIR)[[:space:]]*=[[:space:]]*(.*)[[:space:]]*$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        value="${value#\"}"; value="${value%\"}"
        value="${value#\'}"; value="${value%\'}"
        case "$key" in
          ROOT_AGENTS) ROOT_AGENTS="$value" ;;
          ROOT_COPILOT) ROOT_COPILOT="$value" ;;
          ROOT_CURSOR) ROOT_CURSOR="$value" ;;
          ROOT_ANTIGRAVITY) ROOT_ANTIGRAVITY="$value" ;;
          ROOT_CODEX) ROOT_CODEX="$value" ;;
          ROOT_HERMES) ROOT_HERMES="$value" ;;
          ROOT_OPENCODE) ROOT_OPENCODE="$value" ;;
          ROOT_CMD) ROOT_CMD="$value" ;;
          BACKUP_BASE_DIR) BACKUP_BASE_DIR="$value" ;;
          REPO_DIR) REPO_DIR="$value" ;;
        esac
      else
        echo "Invalid config line in $CONFIG_FILE" >&2
        exit 1
      fi
    done < "$CONFIG_FILE"
  fi

  if [ -z "${REPO_DIR:-}" ] || [ ! -d "$REPO_DIR" ]; then
    REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
  fi
  PY_SCRIPT_DIR="$REPO_DIR/scripts"

  CANONICAL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_HERMES" "$ROOT_OPENCODE" "$ROOT_CMD")
  ALL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_CODEX" "$ROOT_HERMES" "$ROOT_OPENCODE" "$ROOT_CMD")
}

validate_safe_root() {
  local path="$1"
  local label="$2"
  [ -n "$path" ] || { echo "Error: $label is empty" >&2; exit 1; }
  [[ "$path" = /* ]] || { echo "Error: $label must be absolute: $path" >&2; exit 1; }
  [ "$path" != "/" ] || { echo "Error: refusing to use / as $label" >&2; exit 1; }
  [ "$path" != "$HOME" ] || { echo "Error: refusing to use HOME as $label" >&2; exit 1; }
  [ "$path" != "$REPO_DIR" ] || { echo "Error: refusing to use repository root as $label" >&2; exit 1; }
}

validate_skill_name() {
  [[ "$1" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || {
    echo "Error: invalid skill name: $1" >&2
    exit 1
  }
}

validate_repo_spec() {
  # Strict owner/repo to prevent typosquat pulls and flag injection.
  [[ "$1" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || {
    echo "Error: invalid repo spec (expected <owner>/<repo>): $1" >&2
    exit 1
  }
}

validate_backup_dir() {
  local dir="$1"
  [[ "$dir" = /* ]] || { echo "Error: backup directory must be absolute: $dir" >&2; exit 1; }
  [ "$dir" != "/" ] || { echo "Error: refusing to use / as backup directory" >&2; exit 1; }
  [ "$dir" != "$HOME" ] || { echo "Error: refusing to use HOME as backup directory" >&2; exit 1; }
  local base_real
  base_real="$(readlink -f "$BACKUP_BASE_DIR" 2>/dev/null || printf '%s' "$BACKUP_BASE_DIR")"
  local dir_real
  # Resolve parent when dir does not exist yet.
  if [ -e "$dir" ]; then
    dir_real="$(readlink -f "$dir" 2>/dev/null || printf '%s' "$dir")"
  else
    dir_real="$(readlink -f "$(dirname "$dir")" 2>/dev/null || printf '%s' "$(dirname "$dir")")/$(basename "$dir")"
  fi
  case "$dir_real" in
    "$base_real"/*|"$base_real") ;;
    *) echo "Error: backup directory must be inside $BACKUP_BASE_DIR: $dir" >&2; exit 1 ;;
  esac
}

safe_copy_dir() {
  # Copy without propagating setuid/setgid bits or ownership.
  local src="$1" dest="$2"
  if command -v rsync >/dev/null 2>&1; then
    rsync -r --exclude='.git' --chmod=u-s,g-s "$src/" "$dest/"
  else
    if cp --help 2>&1 | grep -q -- '--no-preserve'; then
      cp -a --no-preserve=mode,ownership "$src/." "$dest/"
    else
      cp -a "$src/." "$dest/"
    fi
    chmod -R u-s,g-s "$dest" 2>/dev/null || true
  fi
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
ROOT_HERMES="${DEFAULT_ROOT_HERMES}"
ROOT_OPENCODE="${DEFAULT_ROOT_OPENCODE}"
ROOT_CMD="${DEFAULT_ROOT_CMD}"

# Backup base directory used by: global-skills backup
BACKUP_BASE_DIR="${DEFAULT_BACKUP_BASE_DIR}"

# Repository root directory
REPO_DIR="${REPO_DIR}"
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
  global-skills index
  global-skills generate-commands
  global-skills graph
  global-skills lint
  global-skills telemetry [record|report]
  global-skills generate-docs
  global-skills build-all
  global-skills verify
  global-skills benchmark [--repeats N] [--output FILE]

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
    validate_skill_name "$skill"
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

      safe_copy_dir "$src" "$dest_path"
    done
  done < <(list_canonical_skills)

  echo "Auto-generating commands, index, graph, and docs..."
  python3 "$PY_SCRIPT_DIR/build_index.py"
  python3 "$PY_SCRIPT_DIR/generate_commands.py"
  python3 "$PY_SCRIPT_DIR/dependency_graph.py"
  python3 "$PY_SCRIPT_DIR/generate_docs.py"

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
  validate_backup_dir "$backup_dir"

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
    if [ -L "$root" ]; then
      echo "Warning: skipping symlinked root $root" >&2
      echo "$root -> SKIPPED (symlink)" >> "$backup_dir/manifest.txt"
      continue
    fi
    tar -czf "$backup_dir/${label}.tar.gz" --exclude='.git' -C "$(dirname "$root")" "$(basename "$root")"
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
    count="$(find -L "$root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
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

for configured_root in "${ALL_ROOTS[@]}"; do
  validate_safe_root "$configured_root" "skill root"
done
validate_safe_root "$BACKUP_BASE_DIR" "backup directory"

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
    validate_repo_spec "$repo"

    # Only allow --skill <name> passthrough; reject all other flags to
    # prevent flag injection into npx.
    skill_args=()
    while [ $# -gt 0 ]; do
      case "$1" in
        --skill)
          [ $# -ge 2 ] || { echo "Error: --skill requires a value" >&2; exit 1; }
          validate_skill_name "$2"
          skill_args+=(--skill "$2")
          shift 2
          ;;
        --skill=*)
          validate_skill_name "${1#--skill=}"
          skill_args+=("$1")
          shift
          ;;
        -*)
          echo "Error: unsupported flag for add: $1 (only --skill <name> allowed)" >&2
          exit 1
          ;;
        *)
          echo "Error: unexpected argument for add: $1" >&2
          exit 1
          ;;
      esac
    done

    # Install through Skills CLI, then propagate for full cross-agent parity.
    # NOTE: $repo is validated owner/repo; skill names are validated; no
    # unvalidated passthrough. Pin or review upstream before installing.
    CI=1 npx skills add "$repo" "${skill_args[@]}" -g -y
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
    SRC_REAL="$(readlink -f "$SRC_DIR" 2>/dev/null || printf '%s' "$SRC_DIR")"
    [ "$SRC_REAL" != "/" ] || { echo "Error: refusing to import from /" >&2; exit 1; }
    [ "$SRC_REAL" != "$HOME" ] || { echo "Error: refusing to import from HOME" >&2; exit 1; }

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
      validate_skill_name "$sname"
      echo "  -> Importing $sname"
      rm -rf "$DEST_ROOT/$sname"
      mkdir -p "$DEST_ROOT/$sname"
      safe_copy_dir "$d" "$DEST_ROOT/$sname"
      count=$((count + 1))
    done

    echo "Import complete ($count skills imported)."
    echo "Syncing imported skills across all environments..."
    sync_all
    ;;
  export)
    shift || true
    EXPORT_SCRIPT="$PY_SCRIPT_DIR/export_skills.py"
    if [ ! -f "$EXPORT_SCRIPT" ]; then
      echo "Error: export_skills.py not found at $EXPORT_SCRIPT"
      exit 1
    fi
    python3 "$EXPORT_SCRIPT" --format all --skills-dir "$REPO_DIR/skills" --output-dir "$REPO_DIR/exports"
    python3 "$EXPORT_SCRIPT" --format all --skills-dir "$REPO_DIR/skills" --output-dir "$REPO_DIR"
    ;;
  index)
    python3 "$PY_SCRIPT_DIR/build_index.py"
    ;;
  generate-commands)
    python3 "$PY_SCRIPT_DIR/generate_commands.py"
    ;;
  graph)
    python3 "$PY_SCRIPT_DIR/dependency_graph.py"
    ;;
  lint)
    python3 "$PY_SCRIPT_DIR/lint_skills.py"
    ;;
  telemetry)
    python3 "$PY_SCRIPT_DIR/telemetry.py" "${2:-report}"
    ;;
  generate-docs)
    python3 "$PY_SCRIPT_DIR/generate_docs.py"
    ;;
  search)
    shift || true
    python3 "$PY_SCRIPT_DIR/search_skills.py" "$@"
    ;;
  compose)
    python3 "$PY_SCRIPT_DIR/playbooks.py"
    ;;
  doctor)
    python3 "$PY_SCRIPT_DIR/doctor.py"
    ;;
  explain)
    shift || true
    python3 "$PY_SCRIPT_DIR/doctor.py" explain "$@"
    ;;
  test)
    shift || true
    python3 "$PY_SCRIPT_DIR/test_skills.py" "$@"
    ;;
  orchestrate)
    shift || true
    python3 "$PY_SCRIPT_DIR/orchestrate.py" "$@"
    ;;
  knowledge-graph)
    python3 "$PY_SCRIPT_DIR/build_knowledge_graph.py"
    ;;
  portal)
    python3 "$PY_SCRIPT_DIR/generate_portal.py"
    ;;
  build-all)
    echo "=== [1/9] Building skills.json index... ==="
    python3 "$PY_SCRIPT_DIR/build_index.py"
    echo "=== [2/9] Generating playbooks & compositions... ==="
    python3 "$PY_SCRIPT_DIR/playbooks.py"
    echo "=== [3/9] Auto-generating command wrappers... ==="
    python3 "$PY_SCRIPT_DIR/generate_commands.py"
    echo "=== [4/9] Building dependency graph... ==="
    python3 "$PY_SCRIPT_DIR/dependency_graph.py"
    echo "=== [5/9] Building knowledge graph... ==="
    python3 "$PY_SCRIPT_DIR/build_knowledge_graph.py"
    echo "=== [6/9] Running quality & duplicate linter... ==="
    python3 "$PY_SCRIPT_DIR/lint_skills.py"
    python3 "$PY_SCRIPT_DIR/quality_scorer.py"
    echo "=== [7/9] Auto-generating documentation artifacts & portal... ==="
    python3 "$PY_SCRIPT_DIR/generate_docs.py"
    python3 "$PY_SCRIPT_DIR/generate_portal.py"
    echo "=== [8/9] Exporting multi-client rule files... ==="
    python3 "$PY_SCRIPT_DIR/export_skills.py" --format all --skills-dir "$REPO_DIR/skills" --output-dir "$REPO_DIR/exports"
    python3 "$PY_SCRIPT_DIR/export_skills.py" --format all --skills-dir "$REPO_DIR/skills" --output-dir "$REPO_DIR"
    echo "=== [9/9] Running System Doctor Verification... ==="
    python3 "$PY_SCRIPT_DIR/doctor.py"
    echo "=== Platform Build Complete! ==="
    ;;
  verify)
    python3 "$PY_SCRIPT_DIR/verify_all.py"
    ;;
  benchmark)
    shift || true
    python3 "$PY_SCRIPT_DIR/benchmark.py" "$@"
    ;;
  *)
    usage
    exit 1
    ;;
esac
