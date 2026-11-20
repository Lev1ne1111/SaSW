"""Indexácia. Spúšťa sa raz a potom po každej zmene ontológie alebo PDF.

    python build_index.py
"""
import config
from rag.indexer import embed, load_embedder, save_index
from rag.ontology_loader import load_ontology_chunks
from rag.pdf_loader import load_pdf_chunks


def main():
    # 1. Zdroje znalostí -> textové fragmenty
    onto = load_ontology_chunks()
    pdfs = load_pdf_chunks()
    chunks = onto + pdfs
    print(f"Fragmentov z ontológie: {len(onto)}, z PDF: {len(pdfs)}")

    # 2. Fragmenty -> vektory
    print(f"Načítavam model embeddingov {config.EMBED_MODEL} ...")
    vectors = embed(load_embedder(), [c["text"] for c in chunks])

    # 3. Uloženie
    save_index(chunks, vectors)
    print(f"Hotovo: index je uložený v {config.INDEX_DIR}")


if __name__ == "__main__":
    main()
