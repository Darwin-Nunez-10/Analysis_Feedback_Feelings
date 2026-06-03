# Análisis de Feedback y Sentimiento del Cliente

Sistema de PLN (PID III — Parte 2, Punto 1) para procesar reseñas de e-commerce en español.

## Requisitos

- Python 3.10+
- Conexión a internet en la primera ejecución (descarga modelos spaCy y pysentimiento)

## Instalación

```bash
cd Analysis_Feedback_Feelings
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

Para mayor precisión léxica (recomendado en el rubro del PID):

```bash
python -m spacy download es_core_news_lg
export SPACY_MODEL=es_core_news_lg
```

## Uso

Procesar las muestras incluidas:

```bash
python main.py
```

Procesar un texto personalizado:

```bash
python main.py "El producto llegó tarde y en mal estado"
```

## Pipeline (Punto 1)

1. **Limpieza:** elimina URLs, emails, caracteres especiales y stop words (spaCy español).
2. **Normalización:** tokenización y lematización con spaCy.
3. **Sentimiento:** clasificación Positivo / Neutro / Negativo con [pysentimiento/robertuito](https://huggingface.co/pysentimiento/robertuito-sentiment-analysis).

El análisis de sentimiento se ejecuta sobre el texto limpio (sin lematizar) para preservar negaciones como *"no es bueno"*.

## Estructura

```
src/
  cleaner.py      # limpieza y stop words
  normalizer.py   # tokenización + lematización
  sentiment.py    # análisis de polaridad
  pipeline.py     # orquestación
main.py           # demo CLI
data/muestras.txt # reseñas de prueba
```
