"""Jadro RAG systému. Každý súbor zodpovedá jednej fáze:

ontology_loader.py  – 1a. ontológia (OWL) -> textové karty
pdf_loader.py       – 1b. PDF -> textové fragmenty
indexer.py          – 2.  fragmenty -> vektory (embeddingy), uloženie a načítanie indexu
retriever.py        – R.  hybridné vyhľadávanie relevantných fragmentov
generator.py        – A+G. zostavenie promptu a volanie jazykového modelu
pipeline.py         – spája všetky fázy do jedného celku
"""
