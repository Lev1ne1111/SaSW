"""Všetky nastavenia projektu na jednom mieste."""
from pathlib import Path

# Priečinok, v ktorom leží tento súbor (koreň projektu)
BASE_DIR = Path(__file__).resolve().parent

# --- Zdroje znalostí ---
DATA_DIR = BASE_DIR / "data"
ONTOLOGY_FILE = DATA_DIR / "tanks.owl"   # ontológia z WebProtégé (RDF/XML)
PDF_DIR = DATA_DIR / "pdf"                 # priečinok s PDF dokumentmi

# Jazyk popisov (rdfs:label) z ontológie. Ontológia obsahuje popisy "sk" aj "ru".
LANGUAGE = "sk"

# --- Index ---
# Kam sa uloží hotový index (vytvorí ho skript build_index.py)
INDEX_DIR = BASE_DIR / "index"

# Model embeddingov: mení text na vektor. Je viacjazyčný, rozumie aj slovenčine.
# Pri prvom spustení sa stiahne automaticky (~470 MB).
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Delenie PDF na fragmenty: veľkosť fragmentu a prekrytie (v slovách)
CHUNK_WORDS = 120
CHUNK_OVERLAP = 30

# --- Vyhľadávanie (Retrieval) ---
# Koľko fragmentov sa vyberie z každého zdroja
TOP_K_ONTOLOGY = 3
TOP_K_PDF = 4

# Hybridné vyhľadávanie: váha bonusu za doslovnú zhodu slov otázky s fragmentom.
# 0 = iba sémantické vyhľadávanie pomocou vektorov.
KEYWORD_WEIGHT = 0.3

# --- Generovanie odpovede (Generation) ---
# Ktorý jazykový model formuluje odpoveď: "ollama" (lokálne, zadarmo) alebo "claude" (API)
LLM_PROVIDER = "ollama"

# Ollama: model sa stiahne príkazom  ollama pull qwen3:8b
OLLAMA_MODEL = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"

# Claude: potrebný je kľúč v premennej prostredia ANTHROPIC_API_KEY
# claude-haiku-5-5 je lacný a rýchly; claude-sonnet-5-5 je múdrejší.
CLAUDE_MODEL = "claude-haiku-5-5"
