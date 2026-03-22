#!/usr/bin/env bash
# ローカルで HTTP 402 課金ゲートを有効にして API を起動する。
# 前提: .env に SERPER_API_KEY と STRIPE_SECRET_KEY（テスト用 sk_test_...）が入っていること。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export VERIFY_SKIP_PAYMENT=0
PORT="${PORT:-8000}"
# Checkout の戻り先と uvicorn のポートを一致させる（必要なら事前に PUBLIC_BASE_URL を上書き）
export PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://127.0.0.1:${PORT}}"

exec "${ROOT}/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port "$PORT"
