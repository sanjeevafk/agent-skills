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
@@{PROJECT_ROOT}/requirements.txt NORMAL
@@{PROJECT_ROOT}/requirements-dev.txt NORMAL
@@{PROJECT_ROOT}/requirements-prod.txt NORMAL
@@{PROJECT_ROOT}/pyproject.toml NORMAL
@@{PROJECT_ROOT}/poetry.lock NORMAL
@@{PROJECT_ROOT}/Pipfile NORMAL
@@{PROJECT_ROOT}/Pipfile.lock NORMAL
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

# Full dependency tree — lockfiles are the actual attack surface
FILES=(
  package.json package-lock.json yarn.lock pnpm-lock.yaml
  requirements.txt requirements-dev.txt requirements-prod.txt
  pyproject.toml poetry.lock Pipfile Pipfile.lock
  Gemfile Gemfile.lock go.sum go.mod cargo.lock
  config/env.ts
)

# ---------------------------------------------------------------------------
# Signing helpers — prefer minisign > gpg > plain sha256 (fallback)
# ---------------------------------------------------------------------------
sign_file() {
  local src="$1" out="$2"
  if command -v minisign >/dev/null 2>&1 && [ -f "$HOME/.minisign/minisign.key" ]; then
    minisign -S -m "$src" -s "$HOME/.minisign/minisign.key" -x "${out}.minisig" -q
  elif command -v gpg >/dev/null 2>&1; then
    gpg --batch --yes --detach-sign --armor -o "${out}.asc" "$src"
  else
    sha256sum "$src" > "$out"
  fi
}

verify_file() {
  local src="$1" out="$2"
  if [ -f "${out}.minisig" ] && command -v minisign >/dev/null 2>&1; then
    minisign -V -m "$src" -x "${out}.minisig" -p "$HOME/.minisign/minisign.pub" -q
  elif [ -f "${out}.asc" ] && command -v gpg >/dev/null 2>&1; then
    gpg --batch --verify "${out}.asc" "$src" 2>/dev/null
  else
    # Plain sha256 fallback
    local now old
    now=$(sha256sum "$src" | awk '{print $1}')
    old=$(awk '{print $1}' "$out" 2>/dev/null || echo "")
    [ "$now" = "$old" ]
  fi
}

if [ "${1:-}" = "init" ]; then
  for f in "${FILES[@]}"; do
    [ -f "$PROJECT_ROOT/$f" ] || continue
    out="$INTEGRITY_DIR/${f//\//-}.sha256"
    sha256sum "$PROJECT_ROOT/$f" > "$out"
    sign_file "$PROJECT_ROOT/$f" "$out"
  done
  echo "baseline initialized ($(ls "$INTEGRITY_DIR" | wc -l) files signed)"
  exit 0
fi

changed=0
for f in "${FILES[@]}"; do
  [ -f "$PROJECT_ROOT/$f" ] || continue
  hf="$INTEGRITY_DIR/${f//\//-}.sha256"
  if [ ! -f "$hf" ] && [ ! -f "${hf}.asc" ] && [ ! -f "${hf}.minisig" ]; then
    echo "NO BASELINE: $f — run: bash scripts/security/project/check-integrity.sh init"
    continue
  fi
  if ! verify_file "$PROJECT_ROOT/$f" "$hf"; then
    echo "TAMPERED: $f"
    # Show a meaningful diff for lockfiles and structured files
    if command -v diff >/dev/null 2>&1 && [ -f "$hf" ]; then
      echo "  --- baseline hash    : $(awk '{print $1}' "$hf")"
      echo "  +++ current hash     : $(sha256sum "$PROJECT_ROOT/$f" | awk '{print $1}')"
    fi
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
  echo "=== security scan: \$(date) ==="
  cd "\$PROJECT_ROOT"

  # 1. Tirith — agent runtime: prompt injection, homograph, pipe-to-shell
  if command -v tirith >/dev/null 2>&1; then
    echo "--- tirith"
    tirith scan || true
  elif command -v npx >/dev/null 2>&1; then
    echo "--- tirith (npx)"
    npx --yes @agent-skills/tirith scan || true
  else
    echo "WARN: tirith not installed"
  fi

  # 2. Gitleaks — secret & credential detection (highest ROI)
  if command -v gitleaks >/dev/null 2>&1; then
    echo "--- gitleaks"
    gitleaks detect --source . --no-banner || true
  else
    echo "WARN: gitleaks not installed — brew install gitleaks / https://github.com/gitleaks/gitleaks"
  fi

  # 3. Semgrep — SAST (code-level vulnerability patterns)
  if command -v semgrep >/dev/null 2>&1; then
    echo "--- semgrep"
    semgrep scan --config auto --quiet --error || true
  else
    echo "WARN: semgrep not installed — pip install semgrep / https://semgrep.dev"
  fi

  # 4. Signed dependency-tree integrity
  echo "--- integrity"
  bash scripts/security/project/check-integrity.sh || true

  echo "=== end: \$(date) ==="
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

STAGED=$(git diff --cached --name-only)

# Gitleaks — scan staged changes for secrets before they land in history
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks protect --staged --no-banner || EXIT_CODE=$?
else
  echo "WARN: gitleaks not installed — secrets scan skipped (brew install gitleaks)"
fi

# Tirith — agent config integrity check on dependency file changes
if echo "$STAGED" | grep -Eq '(^|/)package.json$|(^|/)package-lock.json$|(^|/)yarn.lock$|(^|/)pnpm-lock.yaml$|(^|/)requirements.*\.txt$|(^|/)pyproject.toml$|(^|/)poetry.lock$|(^|/)Pipfile(\.lock)?$|(^|/)(go\.sum|go\.mod|Cargo\.lock|Gemfile\.lock)$'; then
  echo "agent-skills: dependency file changed — running security scan"
  if command -v tirith >/dev/null 2>&1; then
    tirith scan || EXIT_CODE=$?
  else
    echo "WARN: tirith not installed — install via docs/TIRITH_SETUP.md"
  fi
fi

exit $EXIT_CODE
HOOK
  chmod +x "$HOOK"
  log_s "Installed pre-commit hook"
fi

log_s "Setup complete"
log_i "Run baseline: bash scripts/security/project/check-integrity.sh init"
log_i "Daily cron: 0 2 * * * $PROJ_DIR/cron-security-checks.sh"
