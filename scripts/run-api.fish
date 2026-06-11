# API FastAPI — backend PLN
set -l ROOT (dirname (status filename))/..
cd $ROOT

if not test -x .venv/bin/uvicorn
    echo "Error: ejecute primero ./scripts/setup.fish"
    exit 1
end

exec .venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
