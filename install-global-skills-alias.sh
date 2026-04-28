#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_SCRIPT="$REPO_ROOT/global-skills.sh"

TARGET_FILE="${HOME}/.bashrc"
ALIAS_NAME="gskills"
ALIAS_LINE="alias ${ALIAS_NAME}='${TARGET_SCRIPT}'"

# Ensure target script exists
if [ ! -f "$TARGET_SCRIPT" ]; then
  echo "Error: global-skills.sh not found at:"
  echo "$TARGET_SCRIPT"
  exit 1
fi

# Ensure .bashrc exists
touch "$TARGET_FILE"

# Add alias only if missing
if grep -Fqx "$ALIAS_LINE" "$TARGET_FILE"; then
  echo "Alias already present in $TARGET_FILE"
else
  echo "" >> "$TARGET_FILE"
  echo "# agent-skills shortcut" >> "$TARGET_FILE"
  echo "$ALIAS_LINE" >> "$TARGET_FILE"
  echo "Added alias '${ALIAS_NAME}' to $TARGET_FILE"
fi

echo
echo "Run this to activate now:"
echo "source ~/.bashrc"
echo
echo "Then test:"
echo "${ALIAS_NAME} status"