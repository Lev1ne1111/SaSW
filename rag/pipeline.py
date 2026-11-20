"""Celý RAG cyklus: vyhľadanie (R) -> prompt (A) -> odpoveď modelu (G)."""
from rag import generator, indexer, retriever


class RAG:
    def __init__(self):
        # Index a model embeddingov sa načítajú iba raz, pri štarte
        self.chunks, self.vectors = indexer.load_index()
        self.embedder = indexer.load_embedder()
        self.llm_ready = generator.is_ready()
        self.model_name = generator.model_name()

    def ask(self, question):
        """Vráti (odpoveď, nájdené fragmenty)."""
        found = retriever.search(question, self.chunks, self.vectors, self.embedder)
        if not self.llm_ready:
            return "Kľúč ANTHROPIC_API_KEY nie je nastavený – zobrazujem iba nájdené fragmenty.", found
        return generator.generate(question, found), found
