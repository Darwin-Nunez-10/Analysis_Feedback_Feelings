"""
Pipeline de Procesamiento de Lenguaje Natural (PLN).

Responsabilidades:
- Limpieza de texto (URLs, caracteres especiales, números, espacios)
- Eliminación de stop words
- Tokenización y lematización con spaCy
"""

from __future__ import annotations

import re

import spacy

# Orden de preferencia de modelos spaCy en español
SPACY_MODELS_PREFERRED = ["es_core_news_lg", "es_core_news_sm"]

# Patrones de limpieza
_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_PATTERN = re.compile(r"\S+@\S+\.\S+")
_NUMBER_PATTERN = re.compile(r"\b\d+\b")
_NON_ALPHA_PATTERN = re.compile(r"[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]+")
_WHITESPACE_PATTERN = re.compile(r"\s+")

_nlp = None
_loaded_model_name: str | None = None


class SpacyModelError(Exception):
    """Error al cargar el modelo de spaCy."""


def load_spacy_model() -> spacy.language.Language:
    """
    Carga el modelo spaCy en español.
    Intenta es_core_news_lg primero; si falla, usa es_core_news_sm.
    """
    global _nlp, _loaded_model_name

    if _nlp is not None:
        return _nlp

    last_error: Exception | None = None
    for model_name in SPACY_MODELS_PREFERRED:
        try:
            _nlp = spacy.load(model_name)
            _loaded_model_name = model_name
            return _nlp
        except OSError as exc:
            last_error = exc

    raise SpacyModelError(
        "No se pudo cargar ningún modelo de spaCy. Instale uno con:\n"
        "  python -m spacy download es_core_news_sm\n"
        "  python -m spacy download es_core_news_lg"
    ) from last_error


def get_loaded_spacy_model_name() -> str | None:
    """Devuelve el nombre del modelo spaCy actualmente cargado."""
    return _loaded_model_name


def remove_urls(text: str) -> str:
    """Elimina URLs del texto."""
    return _URL_PATTERN.sub(" ", text)


def remove_emails(text: str) -> str:
    """Elimina direcciones de correo electrónico."""
    return _EMAIL_PATTERN.sub(" ", text)


def remove_numbers(text: str) -> str:
    """Elimina números aislados (no parte de palabras)."""
    return _NUMBER_PATTERN.sub(" ", text)


def remove_special_chars(text: str) -> str:
    """Elimina caracteres especiales; conserva letras españolas y espacios."""
    text = _NON_ALPHA_PATTERN.sub(" ", text)
    return _WHITESPACE_PATTERN.sub(" ", text).strip()


def normalize_whitespace(text: str) -> str:
    """Colapsa espacios duplicados."""
    return _WHITESPACE_PATTERN.sub(" ", text).strip()


def clean_text(text: str) -> dict:
    """
    Limpia un comentario y elimina stop words con spaCy.

    Returns:
        texto_original: texto de entrada sin modificar (recortado)
        texto_procesado: texto limpio sin stop words (para visualización)
        tokens_sin_stop: tokens alfabéticos sin stop words
        texto_limpio_sentimiento: texto limpio CON stop words (para sentimiento)
    """
    if not text or not str(text).strip():
        return {
            "texto_original": "",
            "texto_procesado": "",
            "tokens_sin_stop": [],
            "texto_limpio_sentimiento": "",
        }

    original = str(text).strip()
    nlp = load_spacy_model()

    # Cadena de limpieza superficial
    cleaned = remove_urls(original)
    cleaned = remove_emails(cleaned)
    cleaned = remove_numbers(cleaned)
    cleaned = remove_special_chars(cleaned)
    cleaned = normalize_whitespace(cleaned)

    # Texto limpio conservando stop words (útil para análisis de sentimiento)
    texto_limpio_sentimiento = cleaned

    doc = nlp(cleaned)
    tokens_sin_stop = [
        token.text.lower()
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
        and len(token.text.strip()) > 1
    ]

    texto_procesado = " ".join(tokens_sin_stop)

    return {
        "texto_original": original,
        "texto_procesado": texto_procesado,
        "tokens_sin_stop": tokens_sin_stop,
        "texto_limpio_sentimiento": texto_limpio_sentimiento,
    }


def lemmatize_tokens(tokens: list[str]) -> dict:
    """
    Tokeniza y lematiza una lista de tokens (ya sin stop words).

    Returns:
        tokens_lematizados: lista de lemas
        texto_lematizado: lemas unidos por espacio
    """
    if not tokens:
        return {
            "tokens_lematizados": [],
            "texto_lematizado": "",
        }

    nlp = load_spacy_model()
    doc = nlp(" ".join(tokens))

    lemmas = []
    for token in doc:
        if token.is_punct or token.is_space:
            continue
        lemma = token.lemma_.lower().strip()
        if lemma and lemma != "-" and lemma not in nlp.Defaults.stop_words:
            lemmas.append(lemma)

    return {
        "tokens_lematizados": lemmas,
        "texto_lematizado": " ".join(lemmas),
    }


def process_text(text: str) -> dict:
    """
    Ejecuta el pipeline completo de PLN sobre un comentario.

    Genera columnas de texto original, procesado y lematizado.
    """
    cleaned = clean_text(text)

    if not cleaned["texto_original"]:
        return {
            "texto_original": "",
            "texto_procesado": "",
            "texto_lematizado": "",
            "tokens_lematizados": [],
            "texto_limpio_sentimiento": "",
        }

    lemmatized = lemmatize_tokens(cleaned["tokens_sin_stop"])

    return {
        "texto_original": cleaned["texto_original"],
        "texto_procesado": cleaned["texto_procesado"],
        "texto_lematizado": lemmatized["texto_lematizado"],
        "tokens_lematizados": lemmatized["tokens_lematizados"],
        "texto_limpio_sentimiento": cleaned["texto_limpio_sentimiento"],
    }


def process_batch(texts: list[str]) -> list[dict]:
    """Procesa una lista de comentarios en lote."""
    return [process_text(t) for t in texts if t and str(t).strip()]
