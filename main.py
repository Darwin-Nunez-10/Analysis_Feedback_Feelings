import sys
from pathlib import Path

from src.pipeline import FeedbackPipeline

MUESTRAS_PATH = Path(__file__).parent / "data" / "muestras.txt"


def load_samples() -> list[str]:
    if not MUESTRAS_PATH.exists():
        return []
    lines = MUESTRAS_PATH.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def print_results(results: list[dict]) -> None:
    col_orig = 40
    col_lem = 35
    col_sent = 12

    header = (
        f"{'ORIGINAL':<{col_orig}} | "
        f"{'LEMATIZADO':<{col_lem}} | "
        f"{'SENTIMIENTO':<{col_sent}} | CONFIANZA"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        orig = r["texto_original"][: col_orig - 2]
        lem = r["texto_lematizado"][: col_lem - 2] or "(vacío)"
        sent = r["sentimiento"]["etiqueta"]
        conf = r["sentimiento"]["confianza"]
        print(
            f"{orig:<{col_orig}} | "
            f"{lem:<{col_lem}} | "
            f"{sent:<{col_sent}} | {conf:.2%}"
        )


def main() -> None:
    pipeline = FeedbackPipeline()

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        results = [pipeline.process(text)]
    else:
        samples = load_samples()
        if not samples:
            print("No hay muestras en data/muestras.txt")
            sys.exit(1)
        results = pipeline.process_batch(samples)

    print_results(results)


if __name__ == "__main__":
    main()
