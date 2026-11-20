"""Fáza R – Retrieval. Hybridné vyhľadávanie relevantných fragmentov.

Skóre fragmentu = sémantická podobnosť (vektory) + bonus za doslovnú zhodu slov.
Malý model embeddingov dobre chápe tému („sovietske tanky“), ale horšie
rozlišuje konkrétne názvy („T-34“). Doslovná zhoda slov to napraví.
"""
import re

import config
from rag.indexer import embed

# Časté slová, ktoré vyhľadávaniu nepomáhajú (nedostávajú bonus)
STOP_WORDS = {"aké", "aký", "aká", "akú", "akého", "ktoré", "ktorý", "ktorá", "čo", "bol", "bola",
              "boli", "bolo", "ako", "kto", "kde", "kedy", "koľko", "pre", "alebo", "jeho", "jej",
              "ich", "tak", "už", "všetky", "všetko", "mal", "mala", "malo", "mali", "majú",
              "ten", "tie", "báze", "bázy", "znalostí"}


def keywords(question):
    """Dôležité slová otázky skrátené na základ.

    Veľmi jednoduchý „stemming“: odrežeme posledné 2 písmená (koncovku),
    ale necháme aspoň 4. Takže „ťažké“ -> „ťažk“ sa nájde aj v „ťažký“.
    """
    words = re.findall(r"[\w-]+", question.lower())
    # set = množina, takže každé slovo sa započíta iba raz
    return {w[:max(4, len(w) - 2)] for w in words if len(w) > 2 and w not in STOP_WORDS}


def keyword_bonus(stems, text):
    """Podiel slov otázky, ktoré sa doslova nachádzajú vo fragmente (0 až 1)."""
    if not stems:
        return 0.0
    text = text.lower()
    return sum(stem in text for stem in stems) / len(stems)


def search(question, chunks, vectors, embedder):
    """Nájde najrelevantnejšie fragmenty – zvlášť z ontológie a zvlášť z PDF."""
    q = embed(embedder, [question])[0]
    similarity = vectors @ q  # kosínusová podobnosť otázky s každým fragmentom
    stems = keywords(question)

    scores = [similarity[i] + config.KEYWORD_WEIGHT * keyword_bonus(stems, c["text"])
              for i, c in enumerate(chunks)]

    # Z každého zdroja vyberieme najlepšie fragmenty, aby boli zastúpené oba
    found = []
    for kind, k in (("ontology", config.TOP_K_ONTOLOGY), ("pdf", config.TOP_K_PDF)):
        ids = [i for i, c in enumerate(chunks) if c["kind"] == kind]
        best = sorted(ids, key=lambda i: scores[i], reverse=True)[:k]
        found += [dict(chunks[i], score=float(scores[i])) for i in best]
    return found
