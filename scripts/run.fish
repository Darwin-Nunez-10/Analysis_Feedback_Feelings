# Ejecuta el dashboard Streamlit (fish shell).
set -l ROOT (dirname (status filename))/..
cd $ROOT

if not test -x .venv/bin/streamlit
    echo "Error: no existe .venv o falta streamlit."
    echo "Ejecute primero: ./scripts/setup.fish"
    exit 1
end

exec .venv/bin/streamlit run app.py $argv
