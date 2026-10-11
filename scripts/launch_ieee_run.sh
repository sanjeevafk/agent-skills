#!/usr/bin/env bash
# One-shot launcher for the IEEE benchmark run.
#
# Usage: bash scripts/launch_ieee_run.sh [backend] [judge_model]
#   Defaults: cmd deepseek/deepseek-v4-pro  (executor + judge via the cmd CLI)
#   agy cross-vendor judge: bash scripts/launch_ieee_run.sh agy claude-sonnet-4-6
#   OpenAI-compatible judge: bash scripts/launch_ieee_run.sh openai <model>
#     and export JUDGE_API_KEY (and JUDGE_BASE_URL if not OpenRouter-compatible).
#
# Credentials are read from the environment, never from a file in the repository.
set -euo pipefail
cd "$(dirname "$0")/.."

EXEC_BACKEND="${EXECUTOR_BACKEND:-cmd}"
EXEC_MODEL="${EXECUTOR_MODEL:-qwen/qwen3.7-flash}"
BACKEND="${1:-${JUDGE_BACKEND:-cmd}}"
JUDGE_MODEL="${2:-${JUDGE_MODEL:-deepseek/deepseek-v4-pro}}"

echo "🚀 Launching IEEE benchmark | executor: ${EXEC_BACKEND}:${EXEC_MODEL} | judge: ${BACKEND}:${JUDGE_MODEL}"

if [ "${BACKEND}" = "cmd" ]; then
  echo "🔎 Judge sanity check (cmd ${JUDGE_MODEL})..."
  REPLY=$(timeout 60 cmd -p "Reply with ONLY the single word OK." --no-session --yolo -m "${JUDGE_MODEL}" 2>&1 | tail -1)
  echo "   -> ${REPLY:0:60}"
  if ! echo "${REPLY}" | grep -qi "ok"; then
    echo "❌ Judge sanity check failed — aborting."
    exit 1
  fi
elif [ "${BACKEND}" = "agy" ]; then
  echo "🔎 Judge sanity check (agy ${JUDGE_MODEL})..."
  REPLY=$(timeout 180 agy --model "${JUDGE_MODEL}" -p "Reply with ONLY the single word OK." 2>&1 | tail -1)
  echo "   -> ${REPLY:0:60}"
  if ! echo "${REPLY}" | grep -qi "ok"; then
    echo "❌ Judge sanity check failed — aborting."
    exit 1
  fi
else
  echo "🔎 OpenAI-judge preflight runs inside the runner."
  if [ -z "${JUDGE_API_KEY:-}" ]; then
    echo "❌ JUDGE_API_KEY is not set. Export it before launching (credentials are"
    echo "   never read from a repository file)."
    exit 1
  fi
fi

mkdir -p benchmarks
LIMIT_ARGS=()
if [ "${JUDGE_LIMIT:-0}" != "0" ]; then
  LIMIT_ARGS=(--judge-limit "${JUDGE_LIMIT}")
  echo "⚖️  Judge limit: ${JUDGE_LIMIT} successful evaluations this invocation"
fi
nohup python3 scripts/skill_delivery_experiment.py \
  --tasks benchmarks/tasks_ieee.json \
  --runs 5 \
  --executor-backend "${EXEC_BACKEND}" \
  --executor-model "${EXEC_MODEL}" \
  --judge-backend "${BACKEND}" \
  --judge-model "${JUDGE_MODEL}" \
  --skip-preflight \
  "${LIMIT_ARGS[@]}" \
  > benchmarks/run_ieee.log 2>&1 &

PID=$!
echo "$PID" > benchmarks/run_ieee.pid
sleep 8
if kill -0 "$PID" 2>/dev/null; then
  echo "✅ Running (pid ${PID}). Monitor: tail -f benchmarks/run_ieee.log"
  head -5 benchmarks/run_ieee.log || true
else
  echo "❌ Process died immediately — log follows:"
  cat benchmarks/run_ieee.log
  exit 1
fi
