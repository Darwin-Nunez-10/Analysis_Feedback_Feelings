"""
Servicios de orquestación para la API REST.

Encapsula el pipeline PLN, sentimiento y métricas sin dependencia de Streamlit.
"""

from __future__ import annotations

import base64
import io
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nlp_pipeline import (
    SpacyModelError,
    get_loaded_spacy_model_name,
    load_spacy_model,
    process_text,
)
from sentiment_analyzer import (
    SentimentModelError,
    analyze_sentiment,
    run_validation_tests,
)
from utils import (
    FileLoadError,
    ValidationError,
    filter_supported_language,
    get_text_columns,
    load_file,
    results_to_dataframe,
    validate_comment_column,
    dataframe_to_csv_bytes,
    dataframe_to_excel_bytes,
)
from visualizations import (
    compute_metrics,
    extract_word_frequencies,
    generate_wordcloud,
    plot_wordcloud_matplotlib,
)


def get_system_status() -> dict[str, Any]:
    """Estado del sistema y modelos cargados."""
    spacy_model = None
    spacy_ok = False
    sentiment_ok = False

    try:
        load_spacy_model()
        spacy_model = get_loaded_spacy_model_name()
        spacy_ok = True
    except SpacyModelError:
        pass

    try:
        from sentiment_analyzer import _get_analyzer

        _get_analyzer()
        sentiment_ok = True
    except SentimentModelError:
        pass

    return {
        "status": "ok" if spacy_ok and sentiment_ok else "degraded",
        "spacy_loaded": spacy_ok,
        "spacy_model": spacy_model,
        "sentiment_loaded": sentiment_ok,
        "sentiment_model": "pysentimiento/robertuito" if sentiment_ok else None,
    }


def preview_file(file_obj, filename: str) -> dict[str, Any]:
    """Carga archivo y devuelve vista previa con columnas candidatas."""
    df = load_file(file_obj, filename)
    text_cols = get_text_columns(df)

    preview_rows = df.head(20).fillna("").astype(str).to_dict(orient="records")
    columns = [str(c) for c in df.columns]

    return {
        "filename": filename,
        "row_count": len(df),
        "columns": columns,
        "text_columns": text_cols,
        "preview": preview_rows,
        "suggested_column": text_cols[0] if len(text_cols) == 1 else None,
    }


def run_full_pipeline(comments: list[str]) -> list[dict]:
    """Ejecuta PLN + sentimiento por comentario."""
    results = []
    for comment in comments:
        nlp_result = process_text(comment)
        if not nlp_result["texto_original"]:
            continue
        text_for_sentiment = (
            nlp_result["texto_limpio_sentimiento"] or nlp_result["texto_original"]
        )
        sentiment = analyze_sentiment(text_for_sentiment)
        results.append({**nlp_result, "sentimiento": sentiment})
    return results


def analyze_file(file_obj, filename: str, column: str) -> dict[str, Any]:
    """Analiza comentarios de un archivo y devuelve resultados completos."""
    load_spacy_model()

    df = load_file(file_obj, filename)
    comments_series = validate_comment_column(df, column)
    valid_comments, rejected = filter_supported_language(comments_series)

    if valid_comments.empty:
        raise ValidationError(
            "No quedaron comentarios válidos. Verifique el idioma o el contenido."
        )

    results = run_full_pipeline(valid_comments.tolist())
    if not results:
        raise ValidationError("No se generaron resultados tras el procesamiento.")

    metrics = compute_metrics(results)
    freq_df = extract_word_frequencies(results, top_n=20)
    word_frequencies = freq_df.to_dict(orient="records") if not freq_df.empty else []

    wordcloud_b64 = _wordcloud_to_base64(results)

    rows = []
    for r in results:
        sent = r.get("sentimiento", {})
        rows.append(
            {
                "comentario_original": r.get("texto_original", ""),
                "comentario_procesado": r.get("texto_procesado", ""),
                "comentario_lematizado": r.get("texto_lematizado", ""),
                "sentimiento": sent.get("etiqueta", ""),
                "confianza": sent.get("confianza", 0.0),
                "probabilidades": sent.get("probabilidades", {}),
            }
        )

    return {
        "metrics": metrics,
        "results": rows,
        "word_frequencies": word_frequencies,
        "wordcloud_base64": wordcloud_b64,
        "excluded_count": int(rejected.shape[0]),
        "excluded_samples": rejected.head(10).tolist(),
        "analyzed_count": len(results),
        "models": {
            "spacy": get_loaded_spacy_model_name(),
            "sentiment": "pysentimiento/robertuito",
        },
    }


def _wordcloud_to_base64(results: list[dict]) -> str | None:
    """Genera imagen PNG de la nube de palabras en base64."""
    wc = generate_wordcloud(results)
    if wc is None:
        return None
    fig = plot_wordcloud_matplotlib(wc)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=120)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def get_validation_results() -> list[dict]:
    """Ejecuta pruebas de negación y sarcasmo."""
    load_spacy_model()
    return run_validation_tests()


def export_results_csv(results: list[dict]) -> bytes:
    """Exporta resultados a CSV."""
    df = results_to_dataframe(_api_rows_to_pipeline(results))
    return dataframe_to_csv_bytes(df)


def export_results_excel(results: list[dict]) -> bytes:
    """Exporta resultados a Excel."""
    df = results_to_dataframe(_api_rows_to_pipeline(results))
    return dataframe_to_excel_bytes(df)


def _api_rows_to_pipeline(rows: list[dict]) -> list[dict]:
    """Convierte filas de la API al formato interno del pipeline."""
    return [
        {
            "texto_original": r.get("comentario_original", ""),
            "texto_procesado": r.get("comentario_procesado", ""),
            "texto_lematizado": r.get("comentario_lematizado", ""),
            "sentimiento": {
                "etiqueta": r.get("sentimiento", ""),
                "confianza": r.get("confianza", 0.0),
                "probabilidades": r.get("probabilidades", {}),
            },
        }
        for r in rows
    ]


# Re-exportar excepciones para la capa HTTP
__all__ = [
    "FileLoadError",
    "ValidationError",
    "SpacyModelError",
    "SentimentModelError",
    "get_system_status",
    "preview_file",
    "analyze_file",
    "get_validation_results",
    "export_results_csv",
    "export_results_excel",
]
