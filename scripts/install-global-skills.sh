#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="$SCRIPT_DIR/global-skills.sh"
TARGET_DIR="${HOME}/.local/bin"
TARGET_BIN="$TARGET_DIR/global-skills"
TARGET_LINK="$TARGET_DIR/skills"
CONFIG_FILE="${HOME}/.global-skills.conf"
ALIAS_LINE="alias skills='global-skills'"

if [ ! -f "$SOURCE_SCRIPT" ]; then
  echo "Error: source script not found: $SOURCE_SCRIPT"
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp "$SOURCE_SCRIPT" "$TARGET_BIN"
chmod +x "$TARGET_BIN"
ln -sf "$TARGET_BIN" "$TARGET_LINK"

echo "Installed binary: $TARGET_BIN (symlinked as $TARGET_LINK)"

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

# Automatically import repository's bundled skills during first installation
REPO_SKILLS_DIR="$(dirname "$SCRIPT_DIR")/skills"
if [ -d "$REPO_SKILLS_DIR" ]; then
  echo
  echo "Found bundled skills in $REPO_SKILLS_DIR. Importing..."
  # Run through the installed binary to guarantee config settings are loaded
  "$TARGET_BIN" import "$REPO_SKILLS_DIR"
fi

echo
echo "Installation complete."
echo "1) Open a new shell (or run: source ~/.bashrc / source ~/.zshrc)"
echo "2) Verify: global-skills status"
echo "3) Shortcut: gskills status"
echo "4) Config: $CONFIG_FILE"
