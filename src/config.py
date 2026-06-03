import os

SPACY_MODEL = os.getenv("SPACY_MODEL", "es_core_news_sm")

SENTIMENT_LABELS = {
    "POS": "Positivo",
    "NEG": "Negativo",
    "NEU": "Neutro",
}
