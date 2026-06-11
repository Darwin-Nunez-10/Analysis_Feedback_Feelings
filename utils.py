"""
Utilidades para carga de archivos, validación de datos y manejo de errores.

Módulo de soporte del dashboard de análisis de feedback.
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import BinaryIO

import pandas as pd

# Extensiones soportadas por el sistema
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt"}

# Patrón básico para detectar texto predominantemente en español/latino
_LATIN_RATIO_THRESHOLD = 0.5
_LATIN_CHARS_PATTERN = re.compile(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]")


class FileLoadError(Exception):
    """Error al cargar o interpretar un archivo de entrada."""


class ValidationError(Exception):
    """Error de validación de datos o columnas."""


def get_file_extension(filename: str) -> str:
    """Obtiene la extensión en minúsculas de un nombre de archivo."""
    return Path(filename).suffix.lower()


def validate_file_extension(filename: str) -> None:
    """Verifica que el archivo tenga una extensión compatible."""
    ext = get_file_extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise FileLoadError(
            f"Formato no compatible: '{ext}'. "
            f"Use uno de: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )


def load_file(uploaded_file: BinaryIO, filename: str) -> pd.DataFrame:
    """
    Carga un archivo CSV, Excel o TXT en un DataFrame.

    Para archivos .txt se asume una línea por comentario.
    """
    validate_file_extension(filename)
    ext = get_file_extension(filename)

    try:
        if ext == ".csv":
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        elif ext == ".txt":
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            df = pd.DataFrame({"comentario": lines})
        else:
            raise FileLoadError(f"Extensión no soportada: {ext}")
    except FileLoadError:
        raise
    except UnicodeDecodeError as exc:
        raise FileLoadError(
            "No se pudo leer el archivo. Verifique la codificación UTF-8."
        ) from exc
    except Exception as exc:
        raise FileLoadError(
            f"El archivo está corrupto o no se pudo procesar: {exc}"
        ) from exc

    if df is None or df.empty:
        raise FileLoadError("El archivo está vacío o no contiene datos.")

    return df


def get_text_columns(df: pd.DataFrame) -> list[str]:
    """Devuelve columnas candidatas que contienen texto."""
    candidates = []
    for col in df.columns:
        series = df[col].dropna().astype(str).str.strip()
        if series.empty:
            continue
        non_empty = series[series != ""]
        if non_empty.empty:
            continue
        # Columna con al menos un valor textual razonable
        avg_len = non_empty.str.len().mean()
        if avg_len >= 3:
            candidates.append(str(col))
    return candidates


def validate_comment_column(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Valida que la columna exista y extrae comentarios no vacíos.

    Returns:
        Serie de comentarios originales (strings).
    """
    if column not in df.columns:
        raise ValidationError(
            f"La columna '{column}' no existe. "
            f"Columnas disponibles: {', '.join(map(str, df.columns))}"
        )

    comments = df[column].fillna("").astype(str).str.strip()
    valid = comments[comments != ""]

    if valid.empty:
        raise ValidationError(
            "No hay comentarios válidos en la columna seleccionada. "
            "Todos los valores están vacíos o nulos."
        )

    return valid


def is_likely_spanish(text: str) -> bool:
    """
    Heurística simple: proporción de caracteres latinos vs. longitud total.
    No reemplaza un detector de idioma formal, pero filtra casos obvios.
    """
    if not text or not text.strip():
        return False
    latin_count = len(_LATIN_CHARS_PATTERN.findall(text))
    ratio = latin_count / max(len(text), 1)
    return ratio >= _LATIN_RATIO_THRESHOLD


def filter_supported_language(comments: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    Separa comentarios en idioma probablemente soportado vs. no soportado.

    Returns:
        (comentarios_válidos, comentarios_rechazados)
    """
    mask = comments.apply(is_likely_spanish)
    return comments[mask], comments[~mask]


def results_to_dataframe(results: list[dict]) -> pd.DataFrame:
    """Convierte la lista de resultados del pipeline a DataFrame exportable."""
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
                "prob_positivo": sent.get("probabilidades", {}).get("POS", 0.0),
                "prob_neutro": sent.get("probabilidades", {}).get("NEU", 0.0),
                "prob_negativo": sent.get("probabilidades", {}).get("NEG", 0.0),
            }
        )
    return pd.DataFrame(rows)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serializa un DataFrame a bytes CSV para descarga en Streamlit."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8")
    return buffer.getvalue().encode("utf-8")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Serializa un DataFrame a bytes Excel para descarga en Streamlit."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return buffer.getvalue()
