#!/usr/bin/env bash
set -euo pipefail

# Install and optionally sync agent-rules-books across agent environments.
# Rules are engineering guidelines (Clean Code, DDD, etc.), not executable skills.

ROOT_AGENTS="${HOME}/.agents/agent-rules-books"
ROOT_COPILOT="${HOME}/.copilot/agent-rules-books"
ROOT_CURSOR="${HOME}/.cursor/agent-rules-books"
ROOT_ANTIGRAVITY="${HOME}/.gemini/antigravity/agent-rules-books"
ROOT_CODEX="${HOME}/.codex/agent-rules-books"

ALL_ROOTS=("$ROOT_AGENTS" "$ROOT_COPILOT" "$ROOT_CURSOR" "$ROOT_ANTIGRAVITY" "$ROOT_CODEX")

usage() {
  cat <<'EOF'
Usage:
  install-rules-books.sh install [--sync]
  install-rules-books.sh sync
  install-rules-books.sh status
  install-rules-books.sh list

Examples:
  install-rules-books.sh install
  install-rules-books.sh install --sync
  install-rules-books.sh sync
  install-rules-books.sh status
  install-rules-books.sh list

What each command does:
  install          Install agent-rules-books from GitHub to ~/.agents/agent-rules-books.
  install --sync   Install AND sync rules to all agent roots.
  sync             Sync rules from ~/.agents/agent-rules-books to all other roots.
  status           Show which agent roots have rules installed.
  list             List all available rules.
EOF
}

install_rules_books() {
  echo "Installing agent-rules-books from GitHub..."
  
  # Use npx skills CLI to install (same as other packages)
  # This installs to ~/.agents but puts agent-rules-books in a special location
  if ! command -v npx &> /dev/null; then
    echo "Error: npx not found. Install Node.js first."
    exit 1
  fi
  
  # The 'add' command will fetch from GitHub and place in agent-rules-books directory
  # Note: agent-rules-books is NOT a skill package, so we handle it manually
  if [ ! -d "$ROOT_AGENTS" ]; then
    echo "Downloading agent-rules-books..."
    mkdir -p "$(dirname "$ROOT_AGENTS")"
    
    # Clone directly since it's reference docs, not a skills package
    git clone https://github.com/ciembor/agent-rules-books.git "$ROOT_AGENTS" 2>/dev/null || {
      echo "Error: Could not clone agent-rules-books repository."
      exit 1
    }
    echo "✓ Installed to $ROOT_AGENTS"
  else
    echo "✓ Already installed at $ROOT_AGENTS"
  fi
  
  # Update if already exists
  if [ -d "$ROOT_AGENTS/.git" ]; then
    cd "$ROOT_AGENTS"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
    cd - > /dev/null
    echo "✓ Updated to latest"
  fi
}

sync_rules_books() {
  if [ ! -d "$ROOT_AGENTS" ]; then
    echo "Error: agent-rules-books not installed at $ROOT_AGENTS"
    echo "Run: install-rules-books.sh install"
    exit 1
  fi
  
  echo "Syncing agent-rules-books to all agent roots..."
  
  for dest_root in "${ALL_ROOTS[@]}"; do
    if [ "$dest_root" = "$ROOT_AGENTS" ]; then
      continue  # Skip source
    fi
    
    mkdir -p "$(dirname "$dest_root")"
    
    if [ -e "$dest_root" ]; then
      rm -rf "$dest_root"
    fi
    
    cp -r "$ROOT_AGENTS" "$dest_root"
    echo "  ✓ $dest_root"
  done
  
  echo "Sync complete."
}

status_rules_books() {
  echo "=== agent-rules-books Installation Status ==="
  echo ""
  
  for root in "${ALL_ROOTS[@]}"; do
    if [ -d "$root" ]; then
      count=$(find "$root" -maxdepth 1 -name "*.md" -type f | wc -l)
      echo "✓ $root ($count rules)"
    else
      echo "✗ $root (not installed)"
    fi
  done
}

list_rules_books() {
  if [ ! -d "$ROOT_AGENTS" ]; then
    echo "Error: agent-rules-books not installed at $ROOT_AGENTS"
    exit 1
  fi
  
  echo "=== Available Rules ==="
  echo ""
  find "$ROOT_AGENTS" -maxdepth 1 -name "*.md" -type f | sort | while read -r file; do
    name=$(basename "$file" .md)
    echo "  • $name"
  done
}

cmd="${1:-}"
case "$cmd" in
  install)
    shift
    if [ "${1:-}" = "--sync" ]; then
      install_rules_books
      sync_rules_books
    else
      install_rules_books
    fi
    ;;
  sync)
    sync_rules_books
    ;;
  status)
    status_rules_books
    ;;
  list)
    list_rules_books
    ;;
  *)
    usage
    exit 1
    ;;
esac
