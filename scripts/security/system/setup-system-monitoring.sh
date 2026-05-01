#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log_i(){ echo -e "${BLUE}INFO${NC}: $*"; }
log_w(){ echo -e "${YELLOW}WARN${NC}: $*"; }
log_s(){ echo -e "${GREEN}OK${NC}: $*"; }

PROJECT_ROOT="${1:-$(pwd)}"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
PROJECT_NAME="$(basename "$PROJECT_ROOT")"
PROJECT_OWNER="$(id -un)"

SEC_DIR="$PROJECT_ROOT/.security"
PROJ_DIR="$SEC_DIR/project"
SYS_DIR="$SEC_DIR/system"
mkdir -p "$PROJ_DIR/hashes" "$PROJ_DIR/logs" "$SYS_DIR"

log_i "Project root: $PROJECT_ROOT"
log_i "Security dir: $SEC_DIR"

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  log_w "Running without root; auditctl/aide install+activation may be skipped"
fi

# System config templates (runtime artifacts; keep out of version control)
cat > "$SYS_DIR/audit-rules.conf" <<RULES
# Generated for $PROJECT_NAME on $(date)
-w $PROJECT_ROOT -p wa -k ${PROJECT_NAME}-changes
-a always,exit -F arch=b64 -S execve -k exec-commands
-a always,exit -F arch=b64 -S socket -F a0=2 -k network-socket
-a always,exit -F arch=b64 -S unlink -S unlinkat -S rename -S renameat -k delete-commands
-w /home/$PROJECT_OWNER/.npm/ -p wa -k npm-cache
RULES
log_s "Wrote $SYS_DIR/audit-rules.conf"

cat > "$SYS_DIR/aide.conf" <<AIDE
# Generated for $PROJECT_NAME on $(date)
@@define PROJECT_ROOT $PROJECT_ROOT
NORMAL = p+i+n+u+g+s+m+c+sha256
@@{PROJECT_ROOT}/package.json NORMAL
@@{PROJECT_ROOT}/package-lock.json NORMAL
@@{PROJECT_ROOT}/yarn.lock NORMAL
@@{PROJECT_ROOT}/pnpm-lock.yaml NORMAL
@@{PROJECT_ROOT}/app/ NORMAL
@@{PROJECT_ROOT}/lib/ NORMAL
@@{PROJECT_ROOT}/scripts/ NORMAL
!@@{PROJECT_ROOT}/node_modules
!@@{PROJECT_ROOT}/.next
AIDE
log_s "Wrote $SYS_DIR/aide.conf"

# Project scripts
cat > "$PROJECT_ROOT/scripts/security/project/check-integrity.sh" <<'INTEGRITY'
#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
INTEGRITY_DIR="$PROJECT_ROOT/.security/project/hashes"
mkdir -p "$INTEGRITY_DIR"
FILES=(package.json package-lock.json yarn.lock pnpm-lock.yaml config/env.ts)

if [ "${1:-}" = "init" ]; then
  for f in "${FILES[@]}"; do
    [ -f "$PROJECT_ROOT/$f" ] && sha256sum "$PROJECT_ROOT/$f" > "$INTEGRITY_DIR/${f//\//-}.sha256"
  done
  echo "baseline initialized"
  exit 0
fi

changed=0
for f in "${FILES[@]}"; do
  [ -f "$PROJECT_ROOT/$f" ] || continue
  hf="$INTEGRITY_DIR/${f//\//-}.sha256"
  [ -f "$hf" ] || { echo "no baseline for $f"; continue; }
  now=$(sha256sum "$PROJECT_ROOT/$f" | awk '{print $1}')
  old=$(awk '{print $1}' "$hf")
  if [ "$now" != "$old" ]; then
    echo "MODIFIED: $f"
    changed=$((changed+1))
  fi
done
[ "$changed" -eq 0 ] && echo "integrity OK" || exit 1
INTEGRITY
chmod +x "$PROJECT_ROOT/scripts/security/project/check-integrity.sh"

cat > "$PROJECT_ROOT/scripts/security/project/monitor-processes.sh" <<'MONITOR'
#!/usr/bin/env bash
set -euo pipefail
while true; do
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "[$ts] non-loopback listeners"
  if command -v ss >/dev/null 2>&1; then
    ss -tlnp 2>/dev/null | awk 'NR==1 || ($4 !~ /127\.0\.0\.1|::1/)'
  else
    netstat -tlnp 2>/dev/null | awk 'NR==1 || ($4 !~ /127\.0\.0\.1|::1/)'
  fi
  echo "[$ts] suspicious processes"
  ps aux | grep -E "curl .*https?://|wget .*https?://|nc .* -l|xmrig|cryptomine" | grep -v grep || true
  sleep 30
done
MONITOR
chmod +x "$PROJECT_ROOT/scripts/security/project/monitor-processes.sh"

cat > "$PROJ_DIR/cron-security-checks.sh" <<CRON
#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$PROJECT_ROOT"
LOG_DIR="\$PROJECT_ROOT/.security/project/logs"
mkdir -p "\$LOG_DIR"
TS=\$(date '+%Y-%m-%d_%H-%M-%S')
LOG="\$LOG_DIR/security-\$TS.log"
{
  echo "start: \$(date)"
  cd "\$PROJECT_ROOT"
  bash scripts/security/security-check.sh || true
  bash scripts/security/supply-chain-check.sh || true
  bash scripts/security/project/check-integrity.sh || true
  echo "end: \$(date)"
} | tee "\$LOG"
CRON
chmod +x "$PROJ_DIR/cron-security-checks.sh"

# Hook chaining (non-destructive)
if [ -d "$PROJECT_ROOT/.git/hooks" ]; then
  HOOK="$PROJECT_ROOT/.git/hooks/pre-commit"
  BACKUP="$PROJECT_ROOT/.git/hooks/pre-commit.security.backup"
  if [ -f "$HOOK" ] && ! grep -q "agent-skills supply-chain security check" "$HOOK"; then
    cp "$HOOK" "$BACKUP"
    log_w "Backed up existing pre-commit hook to $BACKUP"
  fi
  cat > "$HOOK" <<'HOOK'
#!/usr/bin/env bash
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BACKUP="$PROJECT_ROOT/.git/hooks/pre-commit.security.backup"
EXIT_CODE=0
[ -f "$BACKUP" ] && bash "$BACKUP" || true
if git diff --cached --name-only | grep -Eq '(^|/)package.json$|(^|/)package-lock.json$|(^|/)yarn.lock$|(^|/)pnpm-lock.yaml$'; then
  echo "agent-skills supply-chain security check"
  bash "$PROJECT_ROOT/scripts/security/supply-chain-check.sh" || EXIT_CODE=$?
fi
exit $EXIT_CODE
HOOK
  chmod +x "$HOOK"
  log_s "Installed pre-commit hook"
fi

log_s "Setup complete"
log_i "Run baseline: bash scripts/security/project/check-integrity.sh init"
log_i "Daily cron: 0 2 * * * $PROJ_DIR/cron-security-checks.sh"
