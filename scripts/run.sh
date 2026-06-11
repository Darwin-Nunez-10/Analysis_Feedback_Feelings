#!/usr/bin/env bash
# Ejecuta el dashboard Streamlit usando el Python del venv (sin activar).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/streamlit" ]]; then
  echo "Error: no existe .venv o falta streamlit."
  echo "Ejecute primero: ./scripts/setup.sh"
  exit 1
fi

exec "$ROOT/.venv/bin/streamlit" run app.py "$@"
