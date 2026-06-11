"""
Visualizaciones gerenciales para el dashboard de análisis de sentimiento.

Incluye métricas, gráficos de distribución, nube de palabras y tablas.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud

# Colores corporativos para sentimientos
SENTIMENT_COLORS = {
    "Positivo": "#2ecc71",
    "Neutro": "#f39c12",
    "Negativo": "#e74c3c",
}


def compute_metrics(results: list[dict]) -> dict[str, Any]:
    """Calcula métricas generales a partir de los resultados del análisis."""
    total = len(results)
    if total == 0:
        return {
            "total": 0,
            "positivos": 0,
            "neutros": 0,
            "negativos": 0,
            "pct_positivos": 0.0,
            "pct_neutros": 0.0,
            "pct_negativos": 0.0,
        }

    labels = [r["sentimiento"]["etiqueta"] for r in results]
    positivos = labels.count("Positivo")
    neutros = labels.count("Neutro")
    negativos = labels.count("Negativo")

    return {
        "total": total,
        "positivos": positivos,
        "neutros": neutros,
        "negativos": negativos,
        "pct_positivos": round(positivos / total * 100, 1),
        "pct_neutros": round(neutros / total * 100, 1),
        "pct_negativos": round(negativos / total * 100, 1),
    }


def render_metrics_cards(metrics: dict[str, Any]) -> None:
    """Muestra tarjetas de métricas en Streamlit."""
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total analizados", metrics["total"])
    col2.metric("Positivos", metrics["positivos"], f"{metrics['pct_positivos']}%")
    col3.metric("Neutros", metrics["neutros"], f"{metrics['pct_neutros']}%")
    col4.metric("Negativos", metrics["negativos"], f"{metrics['pct_negativos']}%")

    with col5:
        if metrics["total"] > 0:
            balance = metrics["pct_positivos"] - metrics["pct_negativos"]
            st.metric("Balance P−N", f"{balance:+.1f} pp")


def build_sentiment_distribution_df(metrics: dict[str, Any]) -> pd.DataFrame:
    """DataFrame para gráficos de distribución de sentimiento."""
    return pd.DataFrame(
        {
            "Sentimiento": ["Positivo", "Neutro", "Negativo"],
            "Cantidad": [
                metrics["positivos"],
                metrics["neutros"],
                metrics["negativos"],
            ],
            "Porcentaje": [
                metrics["pct_positivos"],
                metrics["pct_neutros"],
                metrics["pct_negativos"],
            ],
        }
    )


def plot_sentiment_bar_plotly(df: pd.DataFrame):
    """Gráfico de barras interactivo con Plotly."""
    color_map = {
        "Positivo": SENTIMENT_COLORS["Positivo"],
        "Neutro": SENTIMENT_COLORS["Neutro"],
        "Negativo": SENTIMENT_COLORS["Negativo"],
    }
    fig = px.bar(
        df,
        x="Sentimiento",
        y="Cantidad",
        color="Sentimiento",
        color_discrete_map=color_map,
        text="Cantidad",
        title="Distribución de sentimientos detectados",
        labels={"Cantidad": "Nº de comentarios"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, height=400)
    return fig


def plot_sentiment_pie_matplotlib(df: pd.DataFrame) -> plt.Figure:
    """Gráfico de pastel con Matplotlib (alternativa estática)."""
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = [SENTIMENT_COLORS[s] for s in df["Sentimiento"]]
    ax.pie(
        df["Cantidad"],
        labels=df["Sentimiento"],
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
    )
    ax.set_title("Proporción de sentimientos")
    fig.tight_layout()
    return fig


def extract_word_frequencies(
    results: list[dict],
    top_n: int = 20,
) -> pd.DataFrame:
    """
    Cuenta las palabras más frecuentes del texto lematizado.
    Excluye tokens vacíos.
    """
    counter: Counter[str] = Counter()
    for r in results:
        tokens = r.get("tokens_lematizados", [])
        if not tokens:
            text = r.get("texto_lematizado", "")
            tokens = text.split() if text else []
        counter.update(t for t in tokens if t and len(t) > 2)

    most_common = counter.most_common(top_n)
    return pd.DataFrame(most_common, columns=["Palabra", "Frecuencia"])


def generate_wordcloud(
    results: list[dict],
    width: int = 800,
    height: int = 400,
) -> WordCloud | None:
    """
    Genera una nube de palabras a partir del texto lematizado.
    Usa stop words en español integradas en WordCloud.
    """
    text = " ".join(
        r.get("texto_lematizado", "")
        for r in results
        if r.get("texto_lematizado")
    )
    if not text.strip():
        return None

    wc = WordCloud(
        width=width,
        height=height,
        background_color="#111827",
        colormap="plasma",
        max_words=150,
        collocations=False,
        stopwords=None,  # ya filtradas en el pipeline spaCy
    ).generate(text)
    return wc


def plot_wordcloud_matplotlib(wc: WordCloud) -> plt.Figure:
    """Renderiza la WordCloud en una figura Matplotlib con fondo oscuro."""
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#111827")
    ax.set_facecolor("#111827")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Nube de palabras (texto lematizado)", color="#e2e8f0", fontsize=12)
    fig.tight_layout()
    return fig


def plot_top_words_bar(freq_df: pd.DataFrame, top_n: int = 10):
    """Gráfico de barras horizontal con las palabras más frecuentes."""
    if freq_df.empty:
        return None
    subset = freq_df.head(top_n)
    fig = px.bar(
        subset,
        x="Frecuencia",
        y="Palabra",
        orientation="h",
        title=f"Top {min(top_n, len(subset))} palabras más frecuentes",
        color="Frecuencia",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=400,
        showlegend=False,
    )
    return fig


def build_results_table(results: list[dict]) -> pd.DataFrame:
    """Tabla comparativa: original, procesado, sentimiento, confianza."""
    rows = []
    for r in results:
        sent = r.get("sentimiento", {})
        rows.append(
            {
                "Comentario original": r.get("texto_original", ""),
                "Comentario procesado": r.get("texto_procesado", ""),
                "Comentario lematizado": r.get("texto_lematizado", ""),
                "Sentimiento": sent.get("etiqueta", ""),
                "Confianza": f"{sent.get('confianza', 0.0):.2%}",
            }
        )
    return pd.DataFrame(rows)


def render_dashboard_results(results: list[dict], chart_type: str = "barras") -> None:
    """
    Renderiza el bloque completo de visualizaciones en Streamlit.

    Args:
        results: lista de dicts del pipeline completo
        chart_type: 'barras' o 'pastel'
    """
    metrics = compute_metrics(results)
    st.subheader("Métricas generales")
    render_metrics_cards(metrics)

    st.subheader("Distribución de sentimiento")
    dist_df = build_sentiment_distribution_df(metrics)

    if chart_type == "pastel":
        fig = plot_sentiment_pie_matplotlib(dist_df)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.plotly_chart(plot_sentiment_bar_plotly(dist_df), use_container_width=True)

    st.subheader("Nube de palabras")
    wc = generate_wordcloud(results)
    if wc:
        fig_wc = plot_wordcloud_matplotlib(wc)
        st.pyplot(fig_wc)
        plt.close(fig_wc)
    else:
        st.info("No hay texto lematizado suficiente para generar la nube de palabras.")

    st.subheader("Palabras clave más frecuentes")
    freq_df = extract_word_frequencies(results, top_n=20)
    if not freq_df.empty:
        tab1, tab2 = st.tabs(["Tabla", "Gráfico"])
        with tab1:
            st.dataframe(freq_df, use_container_width=True, hide_index=True)
        with tab2:
            fig_words = plot_top_words_bar(freq_df, top_n=10)
            if fig_words:
                st.plotly_chart(fig_words, use_container_width=True)
    else:
        st.info("No se encontraron palabras frecuentes tras la lematización.")

    st.subheader("Tabla comparativa de resultados")
    table_df = build_results_table(results)
    st.dataframe(table_df, use_container_width=True, hide_index=True)
