"""Fázy A + G – Augmentation a Generation.

A: nájdené fragmenty sa vložia do promptu spolu s otázkou.
G: jazykový model (Ollama alebo Claude) napíše odpoveď iba podľa týchto faktov.
"""
import json
import os
import re
import urllib.request

import config

SYSTEM_PROMPT = """Si asistent pre bázu znalostí o tankoch.
Odpovedaj po slovensky IBA na základe fragmentov z časti KONTEXT.
Fragmenty sú dvoch druhov: fakty z ontológie a text z PDF dokumentov.
Za každé tvrdenie uveď číslo zdrojového fragmentu v hranatých zátvorkách, napríklad [2].
Ak v kontexte odpoveď nie je, priamo povedz, že táto informácia v báze znalostí nie je. Nič si nevymýšľaj."""


def build_prompt(question, found):
    """A – Augmentation: očíslované fragmenty + otázka."""
    context = "\n\n".join(
        f"[{n}] ({c['source']}, {c['ref']}) {c['text']}"
        for n, c in enumerate(found, start=1)
    )
    return f"KONTEXT:\n{context}\n\nOTÁZKA: {question}"


def model_name():
    """Názov aktuálne použitého jazykového modelu (na zobrazenie)."""
    return config.CLAUDE_MODEL if config.LLM_PROVIDER == "claude" else config.OLLAMA_MODEL


def is_ready():
    """Ollama nepotrebuje kľúč; Claude potrebuje ANTHROPIC_API_KEY."""
    if config.LLM_PROVIDER == "claude":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    return True


def ask_claude(prompt):
    """Volanie Claude cez oficiálnu knižnicu anthropic."""
    import anthropic
    client = anthropic.Anthropic()  # kľúč sa načíta z ANTHROPIC_API_KEY
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def ask_ollama(prompt):
    """Volanie lokálnej Ollamy cez jej HTTP API (bez ďalších knižníc)."""
    body = json.dumps({
        "model": config.OLLAMA_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
        "stream": False,   # čakáme na celú odpoveď naraz
        "think": False,    # pri Qwen3 vypneme režim „premýšľania“ – je to rýchlejšie
    }).encode("utf-8")
    request = urllib.request.Request(config.OLLAMA_URL, data=body,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            answer = json.loads(response.read())["message"]["content"]
    except OSError:
        return "Nepodarilo sa pripojiť k Ollame. Spustite ju (aplikácia Ollama alebo príkaz `ollama serve`)."
    # Pre istotu odstránime blok premýšľania <think>...</think>, ak ho model vrátil
    return re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()


def generate(question, found):
    """G – Generation: pošle prompt zvolenému modelu a vráti odpoveď."""
    prompt = build_prompt(question, found)
    if config.LLM_PROVIDER == "claude":
        return ask_claude(prompt)
    return ask_ollama(prompt)
