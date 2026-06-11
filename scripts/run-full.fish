# Inicia API + frontend Next.js
set -l ROOT (dirname (status filename))/..
cd $ROOT

echo "Iniciando API en http://localhost:8000"
./scripts/run-api.fish &
set -l API_PID $last_pid

function cleanup --on-event fish_exit
    kill $API_PID 2>/dev/null
end

sleep 2
echo "Iniciando frontend en http://localhost:3000"
cd frontend; npm run dev
