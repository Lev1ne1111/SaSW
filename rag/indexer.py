"""Fáza 2. Indexácia: fragmenty -> vektory (embeddingy).

Embedding je zoznam čísel (vektor), ktorý vyjadruje význam textu.
Texty s podobným významom majú podobné vektory.
"""
import json

import numpy as np
from sentence_transformers import SentenceTransformer

import config


def load_embedder():
    """Načíta model embeddingov (pri prvom spustení sa stiahne)."""
    return SentenceTransformer(config.EMBED_MODEL)


def embed(model, texts):
    """Zmení zoznam textov na vektory.

    normalize_embeddings=True: dĺžka každého vektora = 1, potom sa kosínusová
    podobnosť počíta ako obyčajný skalárny súčin.
    """
    return model.encode(texts, normalize_embeddings=True)


def save_index(chunks, vectors):
    """Uloží fragmenty (JSON) a ich vektory (numpy) do priečinka index/."""
    config.INDEX_DIR.mkdir(exist_ok=True)
    np.save(config.INDEX_DIR / "vectors.npy", vectors)
    with open(config.INDEX_DIR / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def load_index():
    """Načíta hotový index. Vráti (fragmenty, vektory)."""
    with open(config.INDEX_DIR / "chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    vectors = np.load(config.INDEX_DIR / "vectors.npy")
    return chunks, vectors
