# Instalación del proyecto (fish shell). No usa source .venv/bin/activate (bash).
set -l ROOT (dirname (status filename))/..
cd $ROOT

set -l PYTHON python3
if not test -d .venv
    echo "==> Creando entorno virtual en .venv ..."
    $PYTHON -m venv .venv
end

echo "==> Instalando dependencias ..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "==> Descargando modelo spaCy (es_core_news_sm) ..."
.venv/bin/python -m spacy download es_core_news_sm

if type -q npm
    echo "==> Instalando dependencias del frontend ..."
    npm --prefix $ROOT/frontend install
    cp -n $ROOT/frontend/.env.local.example $ROOT/frontend/.env.local 2>/dev/null; or true
end

chmod +x $ROOT/scripts/*.fish $ROOT/scripts/*.sh 2>/dev/null; or true

echo ""
echo "Instalación completada."
echo ""
echo "Ejecutar:"
echo "  ./scripts/run-api.fish      # API  → http://localhost:8000"
echo "  ./scripts/run-frontend.fish # Web  → http://localhost:3000"
echo "  ./scripts/run-full.fish     # Ambos"
