#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="$SCRIPT_DIR/global-skills.sh"
TARGET_DIR="${HOME}/.local/bin"
TARGET_BIN="$TARGET_DIR/global-skills"
CONFIG_FILE="${HOME}/.global-skills.conf"
ALIAS_LINE="alias gskills='global-skills'"

if [ ! -f "$SOURCE_SCRIPT" ]; then
  echo "Error: source script not found: $SOURCE_SCRIPT"
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp "$SOURCE_SCRIPT" "$TARGET_BIN"
chmod +x "$TARGET_BIN"

echo "Installed binary: $TARGET_BIN"

if [ ! -f "$CONFIG_FILE" ]; then
  "$TARGET_BIN" init-config
fi

append_if_missing() {
  local file="$1"
  local line="$2"
  touch "$file"
  if ! grep -Fqx "$line" "$file"; then
    echo "$line" >> "$file"
    echo "Updated $file"
  fi
}

PATH_EXPORT='export PATH="$HOME/.local/bin:$PATH"'

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$rc" ] || [ "$rc" = "$HOME/.bashrc" ]; then
    append_if_missing "$rc" ""
    append_if_missing "$rc" "# global-skills"
    append_if_missing "$rc" "$PATH_EXPORT"
    append_if_missing "$rc" "$ALIAS_LINE"
  fi
done

echo
echo "Installation complete."
echo "1) Open a new shell (or run: source ~/.bashrc / source ~/.zshrc)"
echo "2) Verify: global-skills status"
echo "3) Shortcut: gskills status"
echo "4) Config: $CONFIG_FILE"
