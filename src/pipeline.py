from .cleaner import clean
from .normalizer import normalize
from .sentiment import analyze_sentiment


class FeedbackPipeline:
    """Pipeline de PLN: limpieza, normalización y análisis de sentimiento."""

    def process(self, text: str) -> dict:
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")

        cleaned = clean(text)
        normalized = normalize(cleaned["tokens_sin_stop"])
        sentiment = analyze_sentiment(cleaned["texto_limpio"])

        return {
            "texto_original": text.strip(),
            "texto_limpio": cleaned["texto_limpio"],
            "tokens_lematizados": normalized["tokens_lematizados"],
            "texto_lematizado": normalized["texto_lematizado"],
            "sentimiento": sentiment,
        }

    def process_batch(self, texts: list[str]) -> list[dict]:
        return [self.process(t) for t in texts if t and t.strip()]
