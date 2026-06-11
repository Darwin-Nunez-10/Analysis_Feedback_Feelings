#!/usr/bin/env bash
# Instalación del proyecto (bash/zsh). No requiere activar el venv manualmente.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV="$ROOT/.venv"

echo "==> Creando entorno virtual en .venv ..."
"$PYTHON" -m venv "$VENV"

echo "==> Instalando dependencias ..."
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -r requirements.txt

echo "==> Descargando modelo spaCy (es_core_news_sm) ..."
"$VENV/bin/python" -m spacy download es_core_news_sm

if command -v npm >/dev/null 2>&1; then
  echo "==> Instalando dependencias del frontend ..."
  npm --prefix "$ROOT/frontend" install
  cp -n "$ROOT/frontend/.env.local.example" "$ROOT/frontend/.env.local" 2>/dev/null || true
fi

chmod +x "$ROOT"/scripts/*.fish "$ROOT"/scripts/*.sh 2>/dev/null || true

echo ""
echo "Instalación completada."
echo ""
echo "Ejecutar (dos terminales o run-full):"
echo "  ./scripts/run-api.sh      # API  → http://localhost:8000"
echo "  ./scripts/run-frontend.sh # Web  → http://localhost:3000"
echo "  ./scripts/run-full.sh     # Ambos"
