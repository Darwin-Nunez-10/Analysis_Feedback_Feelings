from pysentimiento import create_analyzer

from .config import SENTIMENT_LABELS

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = create_analyzer(task="sentiment", lang="es")
    return _analyzer


def analyze_sentiment(text: str) -> dict:
    """
    Clasifica el texto en Positivo, Neutro o Negativo.

    Debe recibir texto limpio pero sin lematizar para preservar negaciones.
    """
    analyzer = _get_analyzer()
    result = analyzer.predict(text)

    codigo = result.output
    probas = {k: round(float(v), 4) for k, v in result.probas.items()}
    confianza = probas.get(codigo, 0.0)

    return {
        "etiqueta": SENTIMENT_LABELS.get(codigo, codigo),
        "codigo": codigo,
        "confianza": confianza,
        "probabilidades": probas,
    }
