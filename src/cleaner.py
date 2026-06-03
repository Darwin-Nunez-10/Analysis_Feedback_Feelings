import re

import spacy

from .config import SPACY_MODEL

_nlp = None

_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_PATTERN = re.compile(r"\S+@\S+\.\S+")
_NON_ALPHA_PATTERN = re.compile(r"[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]+")
_WHITESPACE_PATTERN = re.compile(r"\s+")


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(SPACY_MODEL)
    return _nlp


def remove_special_chars(text: str) -> str:
    """Elimina URLs, emails y caracteres no alfabéticos; conserva tildes y ñ."""
    text = _URL_PATTERN.sub(" ", text)
    text = _EMAIL_PATTERN.sub(" ", text)
    text = _NON_ALPHA_PATTERN.sub(" ", text)
    text = _WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def clean(text: str) -> dict:
    """
    Limpia el texto y elimina stop words.

    Returns:
        texto_limpio: texto sin caracteres especiales (con stop words, para sentimiento)
        tokens_sin_stop: tokens alfabéticos sin stop words ni puntuación
    """
    nlp = _get_nlp()
    texto_sin_especiales = remove_special_chars(text)
    doc = nlp(texto_sin_especiales)

    tokens_sin_stop = [
        token.text.lower()
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
        and token.text.strip()
    ]

    return {
        "texto_limpio": texto_sin_especiales,
        "tokens_sin_stop": tokens_sin_stop,
    }
