"""
API REST FastAPI — backend del sistema de análisis de feedback.

Expone endpoints consumidos por el frontend Next.js.
"""

from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from api.services import (
    FileLoadError,
    SentimentModelError,
    SpacyModelError,
    ValidationError,
    analyze_file,
    export_results_csv,
    export_results_excel,
    get_system_status,
    get_validation_results,
    preview_file,
)

app = FastAPI(
    title="Análisis de Feedback y Sentimiento",
    description="API PLN + sentimiento para EIF-4200",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExportRequest(BaseModel):
    results: list[dict]


def _handle_errors(exc: Exception) -> HTTPException:
    """Mapea excepciones de dominio a respuestas HTTP claras (heurística Nielsen #9)."""
    if isinstance(exc, FileLoadError):
        return HTTPException(
            status_code=400,
            detail={
                "message": str(exc),
                "solution": "Verifique el formato (.csv, .xlsx, .txt) y que el archivo no esté vacío.",
            },
        )
    if isinstance(exc, ValidationError):
        return HTTPException(
            status_code=422,
            detail={
                "message": str(exc),
                "solution": "Seleccione otra columna o revise que los comentarios contengan texto.",
            },
        )
    if isinstance(exc, SpacyModelError):
        return HTTPException(
            status_code=503,
            detail={
                "message": str(exc),
                "solution": "Ejecute: .venv/bin/python -m spacy download es_core_news_sm",
            },
        )
    if isinstance(exc, SentimentModelError):
        return HTTPException(
            status_code=503,
            detail={
                "message": str(exc),
                "solution": "Verifique la instalación de pysentimiento, transformers y torch.",
            },
        )
    return HTTPException(
        status_code=500,
        detail={
            "message": f"Error interno: {exc}",
            "solution": "Intente de nuevo. Si persiste, reinicie la API.",
        },
    )


@app.get("/api/health")
def health():
    """Estado del sistema — visibilidad para el frontend (Nielsen #1)."""
    return get_system_status()


@app.post("/api/preview")
async def preview(file: UploadFile = File(...)):
    """Vista previa de archivo cargado y columnas detectadas."""
    if not file.filename:
        raise HTTPException(status_code=400, detail={"message": "No se recibió nombre de archivo."})
    try:
        content = await file.read()
        import io

        buffer = io.BytesIO(content)
        return preview_file(buffer, file.filename)
    except Exception as exc:
        raise _handle_errors(exc) from exc


@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    column: str = Form(...),
):
    """Análisis completo de comentarios."""
    if not file.filename:
        raise HTTPException(status_code=400, detail={"message": "Archivo requerido."})
    if not column.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Debe seleccionar la columna de comentarios.",
                "solution": "Elija una columna del listado antes de analizar.",
            },
        )
    try:
        content = await file.read()
        import io

        buffer = io.BytesIO(content)
        return analyze_file(buffer, file.filename, column)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_errors(exc) from exc


@app.get("/api/validation")
def validation():
    """Pruebas de negación y sarcasmo."""
    try:
        return {"tests": get_validation_results()}
    except Exception as exc:
        raise _handle_errors(exc) from exc


@app.post("/api/export/csv")
def export_csv(body: ExportRequest):
    """Descarga resultados en CSV."""
    if not body.results:
        raise HTTPException(status_code=400, detail={"message": "No hay resultados para exportar."})
    data = export_results_csv(body.results)
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=resultados_sentimiento.csv"},
    )


@app.post("/api/export/xlsx")
def export_xlsx(body: ExportRequest):
    """Descarga resultados en Excel."""
    if not body.results:
        raise HTTPException(status_code=400, detail={"message": "No hay resultados para exportar."})
    data = export_results_excel(body.results)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=resultados_sentimiento.xlsx"},
    )
