# Frontend Next.js
set -l ROOT (dirname (status filename))/..
cd $ROOT/frontend

if not test -d node_modules
    echo "Instalando dependencias del frontend..."
    npm install
end

exec npm run dev
