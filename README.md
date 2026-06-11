# Sistema Inteligente de Análisis de Feedback y Sentimiento del Cliente

Proyecto académico **EIF-4200 Inteligencia Artificial I** — dashboard gerencial con **Next.js + React** y backend **FastAPI** para analizar comentarios en español.

## Arquitectura

```
frontend/          → Next.js 16 + React + Tailwind (interfaz)
api/               → FastAPI (REST)
nlp_pipeline.py    → Limpieza, lematización (spaCy)
sentiment_analyzer.py → Sentimiento (pysentimiento)
visualizations.py  → Métricas y WordCloud (servidor)
utils.py           → Carga de archivos y validaciones
```

**Flujo:** Frontend → API REST → Pipeline PLN → Respuesta JSON → Gráficos React

## Requisitos

- Python 3.10+
- Node.js 20+
- ~2 GB para modelos spaCy y sentimiento

## Instalación

### Fish shell (recomendado en CachyOS/Arch)

```fish
cd Analysis_Feedback_Feelings
./scripts/setup.fish
cd frontend && npm install && cd ..
cp frontend/.env.local.example frontend/.env.local
```

### Bash / Zsh

```bash
./scripts/setup.sh
cd frontend && npm install && cd ..
cp frontend/.env.local.example frontend/.env.local
```

## Ejecución

Necesita **dos terminales** (API + frontend) o un solo comando:

### Opción A — Todo en uno (Fish)

```fish
./scripts/run-full.fish
```

### Opción B — Terminales separadas (Fish)

```fish
# Terminal 1 — API Python (puerto 8000)
./scripts/run-api.fish

# Terminal 2 — Frontend Next.js (puerto 3000)
./scripts/run-frontend.fish
```

Abrir: **http://localhost:3000**

### Rutas directas (sin activar venv)

```fish
.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
cd frontend && npm run dev
```

> **Fish:** no use `source .venv/bin/activate` (es Bash). Use `activate.fish` o los scripts anteriores.

## Interfaz (Next.js)

Dashboard profesional basado en las **10 heurísticas de Nielsen**:

| Heurística | Implementación |
|------------|----------------|
| Visibilidad del estado | Indicador de pasos, barra de progreso, badge "Sistema listo" |
| Mundo real | Etiquetas en español claro ("Comentarios de clientes") |
| Control del usuario | Reiniciar, volver atrás, quitar archivo |
| Consistencia | Sistema de diseño unificado (tipografía, colores, botones) |
| Prevención de errores | Validación de formato/tamaño antes de subir |
| Reconocimiento | Columnas visibles, vista previa, filtros en tabla |
| Flexibilidad | Gráfico barras/circular, búsqueda y paginación |
| Minimalismo | Información progresiva por pasos |
| Recuperación de errores | Mensajes con causa y solución |
| Ayuda | Panel lateral de documentación |

## API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado de modelos |
| POST | `/api/preview` | Vista previa de archivo |
| POST | `/api/analyze` | Análisis completo |
| GET | `/api/validation` | Pruebas negación/sarcasmo |
| POST | `/api/export/csv` | Exportar CSV |
| POST | `/api/export/xlsx` | Exportar Excel |

Documentación interactiva: **http://localhost:8000/docs**

## Streamlit (legacy)

La interfaz Streamlit sigue disponible:

```fish
./scripts/run.fish
```

## Archivos de prueba

- `data/muestras.csv`
- `data/muestras.txt`

## Defensa técnica

1. Frontend desacoplado (React) + backend PLN (Python).
2. Sentimiento sobre texto limpio (preserva negaciones).
3. WordCloud y métricas generadas en servidor; gráficos interactivos en cliente.
4. Carga diferida de panel de validación (`dynamic import`).
5. Manejo de errores con mensajes accionables.

## Licencia

Proyecto académico — EIF-4200 Inteligencia Artificial I.
