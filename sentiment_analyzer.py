"""
Análisis de sentimiento en español.

Usa pysentimiento (RoBERTuito) basado en Transformers de Hugging Face.
Clasifica comentarios en Positivo, Neutro o Negativo.
"""

from __future__ import annotations

from typing import Any

# Etiquetas legibles para la interfaz gerencial
SENTIMENT_LABELS = {
    "POS": "Positivo",
    "NEG": "Negativo",
    "NEU": "Neutro",
}

# Ejemplos de validación de negaciones y sarcasmo (requisito académico)
VALIDATION_EXAMPLES = [
    {
        "texto": "El producto es bueno.",
        "tipo": "Afirmación positiva directa",
        "expectativa": "Positivo",
    },
    {
        "texto": "El producto no es bueno.",
        "tipo": "Negación explícita",
        "expectativa": "Negativo",
    },
    {
        "texto": "Excelente servicio, tardaron solo tres semanas.",
        "tipo": "Sarcasmo / ironía",
        "expectativa": "Negativo o Neutro",
    },
    {
        "texto": "Muy mala atención.",
        "tipo": "Opinión negativa directa",
        "expectativa": "Negativo",
    },
    {
        "texto": "No está mal.",
        "tipo": "Negación con matiz positivo",
        "expectativa": "Positivo o Neutro",
    },
    {
        "texto": "El servicio fue rápido y muy eficiente.",
        "tipo": "Afirmación positiva con intensificador",
        "expectativa": "Positivo",
    },
    {
        "texto": "Jamás volvería a comprar aquí.",
        "tipo": "Negación temporal implícita",
        "expectativa": "Negativo",
    },
    {
        "texto": "Qué magnífica compra, llegó completamente roto.",
        "tipo": "Sarcasmo con contraste léxico",
        "expectativa": "Negativo",
    },
    {
        "texto": "El envío tardó, pero el producto cumple lo prometido.",
        "tipo": "Opinión mixta con concesión",
        "expectativa": "Neutro o Positivo",
    },
    {
        "texto": "No recomendaría este producto a nadie.",
        "tipo": "Negación categórica de recomendación",
        "expectativa": "Negativo",
    },
]

_analyzer = None


class SentimentModelError(Exception):
    """Error al cargar o ejecutar el modelo de sentimiento."""


def _get_analyzer():
    """Carga perezosa del analizador pysentimiento para español."""
    global _analyzer
    if _analyzer is None:
        try:
            from pysentimiento import create_analyzer

            _analyzer = create_analyzer(task="sentiment", lang="es")
        except Exception as exc:
            raise SentimentModelError(
                "No se pudo cargar el modelo de sentimiento. "
                "Verifique la instalación de pysentimiento, transformers y torch. "
                f"Detalle: {exc}"
            ) from exc
    return _analyzer


def analyze_sentiment(text: str) -> dict[str, Any]:
    """
    Clasifica el sentimiento de un comentario.

    Se usa texto limpio pero SIN lematizar para preservar negaciones
    (ej.: 'no es bueno' no debe confundirse con 'es bueno').

    Returns:
        etiqueta: Positivo / Neutro / Negativo
        codigo: POS / NEU / NEG
        confianza: probabilidad de la clase predicha
        probabilidades: dict con probabilidades por clase
    """
    if not text or not str(text).strip():
        return {
            "etiqueta": "Neutro",
            "codigo": "NEU",
            "confianza": 0.0,
            "probabilidades": {"POS": 0.0, "NEU": 1.0, "NEG": 0.0},
        }

    try:
        analyzer = _get_analyzer()
        result = analyzer.predict(str(text))
    except SentimentModelError:
        raise
    except Exception as exc:
        raise SentimentModelError(
            f"Error al analizar sentimiento: {exc}"
        ) from exc

    codigo = result.output
    probas = {k: round(float(v), 4) for k, v in result.probas.items()}
    confianza = probas.get(codigo, 0.0)

    return {
        "etiqueta": SENTIMENT_LABELS.get(codigo, codigo),
        "codigo": codigo,
        "confianza": confianza,
        "probabilidades": probas,
    }


def analyze_batch(texts: list[str]) -> list[dict[str, Any]]:
    """Analiza sentimiento de múltiples textos."""
    return [analyze_sentiment(t) for t in texts]


def get_validation_observation(
    texto: str,
    sentimiento: dict[str, Any],
    tipo: str,
    expectativa: str,
) -> str:
    """
    Genera una observación breve sobre negación o sarcasmo
    para la sección de pruebas de validación académica.
    """
    etiqueta = sentimiento.get("etiqueta", "")
    confianza = sentimiento.get("confianza", 0.0)

    if "negación" in tipo.lower():
        if "no" in texto.lower() and "bueno" in texto.lower():
            if etiqueta == "Negativo":
                return (
                    f"El modelo detectó correctamente la negación ({etiqueta}, "
                    f"{confianza:.0%}). La palabra 'no' alteró la polaridad."
                )
            return (
                f"Posible fallo con negación: se esperaba {expectativa}, "
                f"obtuvo {etiqueta} ({confianza:.0%}). "
                "Los modelos pueden confundir 'no es bueno' con positivo."
            )

    if "sarcasmo" in tipo.lower() or "ironía" in tipo.lower():
        if etiqueta in ("Negativo", "Neutro"):
            return (
                f"El modelo parece captar el tono irónico ({etiqueta}, "
                f"{confianza:.0%}). 'Excelente' + demora larga sugiere sarcasmo."
            )
        return (
            f"Posible fallo con sarcasmo: se esperaba {expectativa}, "
            f"obtuvo {etiqueta} ({confianza:.0%}). "
            "El sarcasmo es difícil sin contexto pragmático."
        )

    if "negación con matiz" in tipo.lower():
        if etiqueta in ("Positivo", "Neutro"):
            return (
                f"'No está mal' interpretado como {etiqueta} ({confianza:.0%}). "
                "Expresión coloquial con doble negación suave."
            )
        return (
            f"Interpretación estricta: {etiqueta} ({confianza:.0%}). "
            f"Se esperaba matiz positivo ({expectativa})."
        )

    # Casos directos
    if expectativa.split()[0] == etiqueta or etiqueta in expectativa:
        return f"Clasificación coherente con la expectativa ({etiqueta}, {confianza:.0%})."

    return (
        f"Resultado: {etiqueta} ({confianza:.0%}). "
        f"Expectativa docente: {expectativa}."
    )


def _compute_acierto(etiqueta: str, expectativa: str) -> str:
    """Determina si el resultado coincide con la expectativa académica."""
    opciones = [o.strip() for o in expectativa.split(" o ")]
    return "correcto" if etiqueta in opciones else "incorrecto"


def run_validation_tests(clean_texts: list[str] | None = None) -> list[dict]:
    """
    Ejecuta las pruebas de validación de negación y sarcasmo.

    Args:
        clean_texts: textos ya limpios para sentimiento (misma longitud que ejemplos).
                     Si es None, usa el texto original del ejemplo.
    """
    results = []
    for i, example in enumerate(VALIDATION_EXAMPLES):
        texto = example["texto"]
        text_for_sentiment = (
            clean_texts[i] if clean_texts and i < len(clean_texts) else texto
        )
        sentiment = analyze_sentiment(text_for_sentiment)
        observation = get_validation_observation(
            texto=texto,
            sentimiento=sentiment,
            tipo=example["tipo"],
            expectativa=example["expectativa"],
        )
        results.append(
            {
                "texto_original": texto,
                "tipo_prueba": example["tipo"],
                "expectativa": example["expectativa"],
                "sentimiento": sentiment["etiqueta"],
                "confianza": sentiment["confianza"],
                "probabilidades": sentiment["probabilidades"],
                "acierto": _compute_acierto(sentiment["etiqueta"], example["expectativa"]),
                "observacion": observation,
            }
        )
    return results
