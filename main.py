from __future__ import annotations

from src.pipeline import run_pipeline


def main() -> None:
    summary = run_pipeline()
    print("Comparação Bolsa Família vs BPC por território")
    print("-" * 52)
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
