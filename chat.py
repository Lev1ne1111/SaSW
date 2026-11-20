"""Otázky a odpovede v konzole.

    python chat.py
"""
from rag.pipeline import RAG


def main():
    rag = RAG()
    print(f"Otázky o tankoch (model: {rag.model_name}). Prázdny riadok – koniec.")
    while True:
        question = input("\nOtázka: ").strip()
        if not question:
            break
        answer, found = rag.ask(question)
        print(f"\nOdpoveď:\n{answer}\n\nZdroje:")
        for n, c in enumerate(found, start=1):
            print(f"  [{n}] {c['source']}, {c['ref']} (skóre {c['score']:.2f})")
            if not rag.llm_ready:
                print(f"      {c['text']}")


if __name__ == "__main__":
    main()
