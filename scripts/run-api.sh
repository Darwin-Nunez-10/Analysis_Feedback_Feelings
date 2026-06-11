#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/uvicorn" ]]; then
  echo "Error: ejecute primero ./scripts/setup.sh"
  exit 1
fi

exec "$ROOT/.venv/bin/uvicorn" api.main:app --host 0.0.0.0 --port 8000 --reload
