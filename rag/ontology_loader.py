"""Fáza 1a. Ontológia (OWL) -> textové „karty“.

Jazykový model rozumie textu, nie RDF trojiciam. Preto pre každú inštanciu,
triedu a vlastnosť ontológie zostavíme z jej trojíc krátky popis v slovenčine.
"""
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL

import config

# Názvy štandardných vlastností, ktoré v ontológii nemajú rdfs:label
STANDARD_NAMES = {RDFS.comment: "Komentár", RDFS.seeAlso: "Viac informácií"}


def short(uri):
    """https://example.org/tanks#Tiger_I  ->  Tiger_I"""
    return str(uri).split("#")[-1].split("/")[-1]


def pick_label(g, uri):
    """rdfs:label v nastavenom jazyku (config.LANGUAGE); ak neexistuje, ľubovoľný iný."""
    labels = list(g.objects(uri, RDFS.label))
    for lab in labels:
        if getattr(lab, "language", None) == config.LANGUAGE:
            return str(lab)
    return str(labels[0]) if labels else None


def label(g, uri):
    """Čitateľný názov: rdfs:label, inak krátky názov z URI."""
    if uri in STANDARD_NAMES:
        return STANDARD_NAMES[uri]
    return pick_label(g, uri) or short(uri)


def name(g, uri):
    """Názov spolu s identifikátorom: „Ťažký tank (Heavy_Tank)“."""
    return f"{label(g, uri)} ({short(uri)})"


def parent_chain(g, cls):
    """Všetky nadradené triedy smerom nahor cez rdfs:subClassOf: Heavy_Tank -> Tank.

    Toto je jednoduché logické odvodzovanie: ak je Tiger I ťažký tank
    a ťažký tank je podtrieda tanku, potom je Tiger I tiež tank.
    """
    chain = []
    current = cls
    while True:
        parents = [p for p in g.objects(current, RDFS.subClassOf)
                   if isinstance(p, URIRef) and p != OWL.Thing]
        if not parents or parents[0] in chain:
            return chain
        current = parents[0]
        chain.append(current)


def instances_of(g, cls):
    """Inštancie triedy vrátane inštancií všetkých jej podtried."""
    result = set(g.subjects(RDF.type, cls))
    for sub in g.subjects(RDFS.subClassOf, cls):
        result |= set(instances_of(g, sub))
    return sorted(result, key=lambda x: label(g, x))


def individual_card(g, ind):
    """Karta inštancie, napríklad tanku Tiger I."""
    lines = [f"{name(g, ind)} – objekt ontológie tankov."]

    # Typ objektu spolu so všetkými nadradenými triedami
    for cls in g.objects(ind, RDF.type):
        if cls != OWL.NamedIndividual:
            chain = [cls] + parent_chain(g, cls)
            lines.append("Typ: " + " → ".join(name(g, c) for c in chain) + ".")

    # Všetky ostatné vlastnosti: krajina, výrobca, hmotnosť, kaliber...
    for prop, value in g.predicate_objects(ind):
        if prop in (RDF.type, RDFS.label):
            continue
        # Komentáre v inom jazyku preskočíme
        if getattr(value, "language", None) not in (None, config.LANGUAGE):
            continue
        # Ak je hodnota iný objekt, použijeme jeho názov (ZSSR, Henschel...).
        # Ak je to číslo alebo text (aj URL odkaz), použijeme ho tak, ako je.
        text = pick_label(g, value) or value
        lines.append(f"{label(g, prop)}: {str(text).rstrip('.')}.")

    return " ".join(lines)


def class_card(g, cls):
    """Karta triedy, napríklad „Ťažký tank“ so zoznamom všetkých ťažkých tankov."""
    lines = [f"Trieda ontológie „{label(g, cls)}“ ({short(cls)})."]

    parents = parent_chain(g, cls)
    if parents:
        lines.append("Je podtriedou: " + " → ".join(name(g, p) for p in parents) + ".")

    subclasses = list(g.subjects(RDFS.subClassOf, cls))
    if subclasses:
        lines.append("Podtriedy: " + ", ".join(name(g, s) for s in subclasses) + ".")

    members = instances_of(g, cls)
    if members:
        lines.append(f"Inštancie ({len(members)}): " + ", ".join(label(g, m) for m in members) + ".")
    else:
        lines.append("Táto trieda nemá v ontológii žiadne inštancie.")

    return " ".join(lines)


def property_card(g, prop):
    """Karta vlastnosti, napríklad hasWeight: čo s čím spája."""
    domain = g.value(prop, RDFS.domain)
    rng = g.value(prop, RDFS.range)
    return (f"Vlastnosť ontológie „{label(g, prop)}“ ({short(prop)}). "
            f"Vzťahuje sa na: {name(g, domain) if domain else '—'}. "
            f"Hodnota: {name(g, rng) if rng else '—'}.")


def load_ontology_chunks():
    """Načíta ontológiu a vráti zoznam kariet (fragmentov)."""
    g = Graph()
    g.parse(config.ONTOLOGY_FILE, format="xml")  # WebProtégé exportuje RDF/XML

    chunks = []

    def add(text, uri):
        chunks.append({"kind": "ontology", "source": "ontológia", "ref": short(uri), "text": text})

    for ind in sorted(set(g.subjects(RDF.type, OWL.NamedIndividual))):
        add(individual_card(g, ind), ind)

    for cls in sorted(set(g.subjects(RDF.type, OWL.Class))):
        if isinstance(cls, URIRef):
            add(class_card(g, cls), cls)

    for prop_type in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for prop in sorted(set(g.subjects(RDF.type, prop_type))):
            add(property_card(g, prop), prop)

    return chunks
