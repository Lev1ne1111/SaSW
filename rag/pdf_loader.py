"""Fáza 1b. PDF -> textové fragmenty (chunks).

Celý dokument je príliš dlhý na presné vyhľadávanie, preto sa text každej
strany rozdelí na kúsky po ~120 slov. Susedné kúsky sa prekrývajú o 30 slov,
aby sa myšlienka na hranici nestratila.
"""
import re

from pypdf import PdfReader

import config


def clean(text):
    """Odstráni hlavičky/päty strán a nadbytočné medzery a zalomenia riadkov."""
    text = re.sub(r"Báza znalostí „Tanky“ · KB-\d+", " ", text)
    text = re.sub(r"str\. \d+", " ", text)
    return " ".join(text.split())


def split_words(text, size, overlap):
    """Rozdelí text na kúsky po `size` slov s prekrytím `overlap` slov."""
    words = text.split()
    step = size - overlap
    pieces = []
    for start in range(0, max(len(words) - overlap, 1), step):
        piece = " ".join(words[start:start + size])
        if piece:
            pieces.append(piece)
    return pieces


def load_pdf_chunks():
    """Načíta všetky PDF z priečinka a vráti zoznam fragmentov."""
    chunks = []
    for pdf_path in sorted(config.PDF_DIR.glob("*.pdf")):
        reader = PdfReader(pdf_path)
        title = (reader.metadata.title if reader.metadata else None) or pdf_path.stem

        for page_number, page in enumerate(reader.pages, start=1):
            text = clean(page.extract_text() or "")
            for piece in split_words(text, config.CHUNK_WORDS, config.CHUNK_OVERLAP):
                chunks.append({
                    "kind": "pdf",
                    "source": pdf_path.name,
                    "ref": f"str. {page_number}",
                    # Názov dokumentu pomáha vyhľadávaniu pochopiť, o čom fragment je
                    "text": f"[{title}] {piece}",
                })
    return chunks
