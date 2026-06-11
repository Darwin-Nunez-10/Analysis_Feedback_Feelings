#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Iniciando API en http://localhost:8000"
"$ROOT/scripts/run-api.sh" &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT

sleep 2
echo "Iniciando frontend en http://localhost:3000"
cd "$ROOT/frontend" && npm run dev
