# RAG systém „Tanky“: ontológia + PDF + jazykový model

Systém odpovedá na otázky o tankoch a opiera sa pritom o dva zdroje znalostí:
- **ontológiu** `data/tanks.owl` (triedy, inštancie a vlastnosti z WebProtégé);
- **10 PDF dokumentov** v priečinku `data/pdf/`.

Odpoveď formuluje jazykový model: lokálny **Qwen3 cez Ollamu** (zadarmo) alebo **Claude cez API**.

## Dáta

Dáta nie sú súčasťou repozitára. Pred spustením ich treba vložiť do priečinka `data/`:

```
data/
├── tanks.owl     ontológia (export z WebProtégé, RDF/XML)
└── pdf/          PDF dokumenty
```

## Inštalácia (raz)

```powershell
pip install -r requirements.txt
```

Jazykový model sa vyberá v `config.py` (`LLM_PROVIDER`):

- **`"ollama"`** (predvolené) – zadarmo a lokálne. Treba nainštalovanú Ollamu a model
  `ollama pull qwen3:8b`. Aplikácia Ollama musí bežať.
- **`"claude"`** – cez API. Treba kľúč: `setx ANTHROPIC_API_KEY "sk-ant-..."`
  (potom reštartovať terminál). Bez kľúča systém iba zobrazí nájdené fragmenty.

## Spustenie

```powershell
python build_index.py      # 1. vytvorenie indexu (raz a po každej zmene ontológie/PDF)
python chat.py             # 2a. otázky v konzole
streamlit run app.py       # 2b. alebo webové rozhranie v prehliadači
```

Pri prvom spustení sa stiahne model embeddingov (~470 MB).

## Štruktúra projektu

```
SaSW/
├── config.py              všetky nastavenia
├── build_index.py         spustenie: indexácia
├── chat.py                spustenie: konzola
├── app.py                 spustenie: webové rozhranie (Streamlit)
├── requirements.txt       potrebné knižnice
├── data/
│   ├── tanks.owl          ontológia (popisy v slovenčine aj ruštine)
│   └── pdf/               10 PDF dokumentov
├── index/                 vytvorí build_index.py
└── rag/                   jadro systému – každý súbor = jedna fáza
    ├── ontology_loader.py 1a. ontológia → textové karty
    ├── pdf_loader.py      1b. PDF → textové fragmenty
    ├── indexer.py         2.  fragmenty → vektory, uloženie/načítanie indexu
    ├── retriever.py       R.  hybridné vyhľadávanie
    ├── generator.py       A+G. prompt + volanie Ollama/Claude
    └── pipeline.py        spája všetky fázy dokopy
```

## Ako to funguje

### Fáza 1. Načítanie znalostí (`rag/ontology_loader.py`, `rag/pdf_loader.py`)

**Ontológia → karty.** Knižnica `rdflib` načíta OWL súbor ako graf RDF trojíc. Z trojíc každého
objektu sa zostaví text, napríklad pre Tiger I:
> Tiger I (Tiger_I) – objekt ontológie tankov. Typ: Ťažký tank (Heavy_Tank) → Model tanku (Tank).
> Vyrábala spoločnosť: Henschel. Hmotnosť, t: 57. ...

Spolu vznikne 60 kariet: 30 pre inštancie, 19 pre triedy a 11 pre vlastnosti. Pri tom sa využívajú dve vlastnosti sémantického webu:
- **Logické odvodzovanie cez `rdfs:subClassOf`.** Tiger I je zapísaný ako `Heavy_Tank`, ale systém vie,
  že je to zároveň `Tank`. Preto karta triedy „Model tanku“ obsahuje všetkých 10 tankov,
  hoci ani jeden nie je priradený priamo k triede `Tank`.
- **Viacjazyčné popisy (`xml:lang`).** Každý `rdfs:label` je v ontológii po slovensky (`sk`)
  aj po rusky (`ru`). Systém berie jazyk nastavený v `config.LANGUAGE`.

**PDF → fragmenty.** Text každej strany sa rozdelí na kúsky po 120 slov s prekrytím 30 slov,
aby sa veta na hranici nestratila.

### Fáza 2. Indexácia (`rag/indexer.py`)

Každý fragment sa modelom `paraphrase-multilingual-MiniLM-L12-v2` zmení na vektor s 384 číslami
(embedding). Texty s podobným významom majú blízke vektory. Vektory sa uložia do `index/vectors.npy`
a texty do `index/chunks.json`.

### Fáza R – Retrieval (`rag/retriever.py`)

Skóre každého fragmentu má dve časti:
1. **Sémantická podobnosť.** Aj otázka sa zmení na vektor a vypočíta sa **kosínusová podobnosť**
   s každým fragmentom. Vektory sú normalizované, preto je to obyčajný skalárny súčin.
2. **Bonus za doslovnú zhodu slov.** Z otázky sa vezmú dôležité slová: časté slová ako „aký“ či „ktoré“ sa vynechajú
   a ostatným sa odreže koncovka („ťažké“ → „ťažk“). Bonus = podiel týchto slov,
   ktoré sa nachádzajú vo fragmente, vynásobený hodnotou `KEYWORD_WEIGHT` (0,3).

Prečo bonus: malý model embeddingov dobre chápe tému („sovietske tanky“),
ale horšie rozlišuje konkrétne názvy („T-34“). Doslovná zhoda to napraví.

Vyberú sa 3 najlepšie fragmenty z ontológie a 4 najlepšie z PDF. Vyhľadáva sa zvlášť v každom zdroji,
takže v odpovedi sú vždy zastúpené oba.

### Fázy A + G – Augmentation a Generation (`rag/generator.py`)

- **A:** nájdené fragmenty sa očíslujú a vložia do promptu spolu s otázkou.
- **G:** prompt sa pošle jazykovému modelu: lokálnemu Qwen3 cez HTTP API Ollamy (`localhost:11434`)
  alebo Claude cez API. Model dostane inštrukciu odpovedať iba podľa kontextu,
  uvádzať čísla zdrojov `[1]` a priznať, ak odpoveď nepozná.

## Prečo dva zdroje

V ontológii sú presné štruktúrované fakty: kto tank vyrábal, do ktorej triedy patrí,
číselné vlastnosti (vyplnené pre T-34-85 a Tiger I). V PDF sú opisy, história a parametre,
ktoré v ontológii nie sú. Príklady otázok na ukážku:

| Otázka | Odkiaľ je odpoveď |
|---|---|
| Ktoré ťažké tanky sú v ontológii? | ontológia (trieda `Heavy_Tank`) |
| Kto vyrábal Tiger I a akú mal hmotnosť? | ontológia |
| Akú hmotnosť má Leopard 2 a aký má motor? | PDF (v ontológii hmotnosť chýba) |
| Čo je reaktívny pancier? | PDF |
| Ktoré tanky ZSSR sú v báze a čím bol známy T-34? | oba zdroje |
| Koľko stojí tank Abrams? | nikde – systém má povedať, že to nevie |

## Možné vylepšenia

- vektorová databáza (Chroma, Qdrant) namiesto numpy – potrebná pri tisícoch dokumentov;
- generovanie SPARQL dopytov z otázky pre presné výbery („všetky tanky ťažšie ako 50 t“);
- výkonnejší model embeddingov (`BAAI/bge-m3`).
