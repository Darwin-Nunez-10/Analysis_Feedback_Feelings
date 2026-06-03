import spacy

from .config import SPACY_MODEL

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(SPACY_MODEL)
    return _nlp


def normalize(tokens: list[str]) -> dict:
    """
    Tokeniza y lematiza una lista de tokens (sin stop words).

    Returns:
        tokens_originales: tokens de entrada en minúsculas
        tokens_lematizados: lemas spaCy
        texto_lematizado: lemas unidos por espacio
    """
    if not tokens:
        return {
            "tokens_originales": [],
            "tokens_lematizados": [],
            "texto_lematizado": "",
        }

    nlp = _get_nlp()
    texto = " ".join(tokens)
    doc = nlp(texto)

    tokens_originales = []
    tokens_lematizados = []

    for token in doc:
        if token.is_punct or token.is_space:
            continue
        tokens_originales.append(token.text.lower())
        lemma = token.lemma_.lower().strip()
        if lemma and lemma != "-":
            tokens_lematizados.append(lemma)

    return {
        "tokens_originales": tokens_originales,
        "tokens_lematizados": tokens_lematizados,
        "texto_lematizado": " ".join(tokens_lematizados),
    }
