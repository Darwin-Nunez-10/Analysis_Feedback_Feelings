"""
Dashboard Streamlit — Sistema Inteligente de Análisis de Feedback y Sentimiento.

EIF-4200 Inteligencia Artificial I
Interfaz principal: carga de datos, análisis PLN, visualización gerencial.
"""

from __future__ import annotations

import streamlit as st

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
    dataframe_to_csv_bytes,
    dataframe_to_excel_bytes,
    filter_supported_language,
    get_text_columns,
    load_file,
    results_to_dataframe,
    validate_comment_column,
)
from visualizations import render_dashboard_results

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Análisis de Feedback y Sentimiento",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos mínimos para presentación académica
st.markdown(
    """
    <style>
    .main-header { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
    .sub-header { color: #4a4a6a; margin-bottom: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def run_full_pipeline(comments: list[str]) -> list[dict]:
    """
    Orquesta PLN + sentimiento para cada comentario.

    El sentimiento se calcula sobre texto limpio (con stop words)
    para preservar negaciones como 'no es bueno'.
    """
    results = []
    for comment in comments:
        nlp_result = process_text(comment)
        if not nlp_result["texto_original"]:
            continue

        text_for_sentiment = (
            nlp_result["texto_limpio_sentimiento"]
            or nlp_result["texto_original"]
        )
        sentiment = analyze_sentiment(text_for_sentiment)

        results.append(
            {
                **nlp_result,
                "sentimiento": sentiment,
            }
        )
    return results


def render_sidebar() -> dict:
    """Panel lateral: carga de archivo y opciones."""
    st.sidebar.title("Configuración")
    st.sidebar.markdown("Cargue comentarios de clientes en **CSV**, **Excel** o **TXT**.")

    uploaded = st.sidebar.file_uploader(
        "Seleccionar archivo",
        type=["csv", "xlsx", "xls", "txt"],
        help="Un comentario por línea en archivos .txt",
    )

    chart_type = st.sidebar.radio(
        "Tipo de gráfico de distribución",
        options=["barras", "pastel"],
        format_func=lambda x: "Barras (Plotly)" if x == "barras" else "Pastel (Matplotlib)",
    )

    return {
        "uploaded_file": uploaded,
        "chart_type": chart_type,
    }


def render_upload_section(uploaded_file) -> tuple | None:
    """
    Carga y previsualización de datos.
    Returns: (df, columna_seleccionada) o None si no hay archivo.
    """
    if uploaded_file is None:
        st.info("👈 Cargue un archivo desde el panel lateral para comenzar.")
        return None

    try:
        df = load_file(uploaded_file, uploaded_file.name)
    except FileLoadError as exc:
        st.error(str(exc))
        return None

    st.subheader("Vista previa de datos cargados")
    st.caption(f"Archivo: **{uploaded_file.name}** — {len(df)} filas, {len(df.columns)} columnas")
    st.dataframe(df.head(20), use_container_width=True)

    text_cols = get_text_columns(df)
    if not text_cols:
        st.error(
            "No se detectaron columnas con texto válido. "
            "Verifique que el archivo contenga comentarios."
        )
        return None

    if len(text_cols) == 1:
        selected_col = text_cols[0]
        st.success(f"Columna de comentarios detectada: **{selected_col}**")
    else:
        selected_col = st.selectbox(
            "Seleccione la columna que contiene los comentarios",
            options=text_cols,
        )

    return df, selected_col


def render_validation_section() -> None:
    """Sección académica: pruebas de negación y sarcasmo."""
    st.subheader("Pruebas de validación")
    st.caption(
        "Ejemplos controlados para evaluar cómo el modelo interpreta "
        "negaciones, ironía y expresiones coloquiales."
    )

    if st.button("Ejecutar pruebas de validación", key="btn_validation"):
        with st.spinner("Procesando ejemplos de validación..."):
            try:
                load_spacy_model()
                validation_results = run_validation_tests()
            except (SpacyModelError, SentimentModelError) as exc:
                st.error(str(exc))
                return

        import pandas as pd

        val_df = pd.DataFrame(validation_results)
        st.dataframe(
            val_df[
                [
                    "texto_original",
                    "tipo_prueba",
                    "expectativa",
                    "sentimiento",
                    "confianza",
                    "observacion",
                ]
            ].rename(
                columns={
                    "texto_original": "Texto original",
                    "tipo_prueba": "Tipo de prueba",
                    "expectativa": "Expectativa",
                    "sentimiento": "Sentimiento detectado",
                    "confianza": "Confianza",
                    "observacion": "Observación",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


def main() -> None:
    """Punto de entrada del dashboard."""
    st.markdown('<p class="main-header">Sistema de Análisis de Feedback y Sentimiento</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">EIF-4200 · Inteligencia Artificial I · '
        "Dashboard gerencial de comentarios de clientes</p>",
        unsafe_allow_html=True,
    )

    sidebar_opts = render_sidebar()
    upload_result = render_upload_section(sidebar_opts["uploaded_file"])

    # Información de modelos cargados (si ya se ejecutó análisis)
    if "models_info" in st.session_state:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Modelos activos**")
        st.sidebar.text(st.session_state["models_info"])

    # -----------------------------------------------------------------------
    # Análisis por lote
    # -----------------------------------------------------------------------
    if upload_result is not None:
        df, comment_col = upload_result

        if st.button("Ejecutar análisis", type="primary", use_container_width=True):
            try:
                comments_series = validate_comment_column(df, comment_col)
            except ValidationError as exc:
                st.error(str(exc))
                return

            valid_comments, rejected = filter_supported_language(comments_series)

            if rejected.shape[0] > 0:
                st.warning(
                    f"{rejected.shape[0]} comentario(s) posiblemente en idioma no soportado "
                    "fueron excluidos del análisis."
                )
                with st.expander("Ver comentarios excluidos"):
                    st.write(rejected.tolist())

            if valid_comments.empty:
                st.error(
                    "No quedaron comentarios válidos para analizar. "
                    "Revise el idioma o el contenido del archivo."
                )
                return

            progress = st.progress(0, text="Inicializando modelos de PLN y sentimiento...")

            try:
                load_spacy_model()
                progress.progress(20, text="Modelo spaCy cargado. Analizando comentarios...")
                results = run_full_pipeline(valid_comments.tolist())
                progress.progress(100, text="Análisis completado.")
            except SpacyModelError as exc:
                st.error(str(exc))
                return
            except SentimentModelError as exc:
                st.error(str(exc))
                return
            except Exception as exc:
                st.error(f"Error inesperado durante el análisis: {exc}")
                return
            finally:
                progress.empty()

            if not results:
                st.error("No se generaron resultados. Verifique que los textos no estén vacíos.")
                return

            st.session_state["analysis_results"] = results
            st.session_state["models_info"] = (
                f"spaCy: {get_loaded_spacy_model_name() or 'N/A'}\n"
                "Sentimiento: pysentimiento/robertuito"
            )
            st.success(f"Se analizaron **{len(results)}** comentarios correctamente.")

    # -----------------------------------------------------------------------
    # Resultados y descarga
    # -----------------------------------------------------------------------
    if "analysis_results" in st.session_state:
        results = st.session_state["analysis_results"]

        st.markdown("---")
        render_dashboard_results(results, chart_type=sidebar_opts["chart_type"])

        st.markdown("---")
        st.subheader("Descargar resultados")
        export_df = results_to_dataframe(results)

        col_csv, col_xlsx = st.columns(2)
        with col_csv:
            st.download_button(
                label="Descargar CSV",
                data=dataframe_to_csv_bytes(export_df),
                file_name="resultados_sentimiento.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_xlsx:
            st.download_button(
                label="Descargar Excel",
                data=dataframe_to_excel_bytes(export_df),
                file_name="resultados_sentimiento.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # -----------------------------------------------------------------------
    # Validación académica (siempre visible)
    # -----------------------------------------------------------------------
    st.markdown("---")
    render_validation_section()

    # Arquitectura (pie de página para defensa técnica)
    with st.expander("Arquitectura del sistema"):
        st.markdown(
            """
            | Módulo | Responsabilidad |
            |--------|-----------------|
            | `app.py` | Interfaz Streamlit, orquestación y descarga |
            | `nlp_pipeline.py` | Limpieza, tokenización, lematización (spaCy) |
            | `sentiment_analyzer.py` | Clasificación Pos/Neu/Neg (pysentimiento) |
            | `visualizations.py` | Métricas, gráficos, WordCloud, tablas |
            | `utils.py` | Carga de archivos, validaciones, exportación |

            **Flujo:** Carga → Validación → Limpieza → Lematización → Sentimiento → Visualización → Exportación
            """
        )


if __name__ == "__main__":
    main()
