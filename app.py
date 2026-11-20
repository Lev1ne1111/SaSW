"""Webové rozhranie.

    streamlit run app.py
"""
import streamlit as st

from rag.pipeline import RAG

st.set_page_config(page_title="RAG: tanky", page_icon="🛡️")
st.title("Otázky o tankoch")
st.caption("Zdroje znalostí: ontológia tanks.owl + 10 PDF dokumentov")


@st.cache_resource  # model a index sa načítajú iba raz, nie pri každej otázke
def get_rag():
    return RAG()


rag = get_rag()
st.caption(f"Jazykový model: {rag.model_name}")
if not rag.llm_ready:
    st.warning("Kľúč ANTHROPIC_API_KEY nie je nastavený – zobrazia sa iba nájdené fragmenty.")

question = st.text_input("Vaša otázka", placeholder="Napríklad: Kto vyrábal Tiger I a akú mal hmotnosť?")

if question:
    with st.spinner("Hľadám odpoveď..."):
        answer, found = rag.ask(question)

    st.markdown(answer)

    st.subheader("Nájdené fragmenty")
    for n, c in enumerate(found, start=1):
        icon = "🔷" if c["kind"] == "ontology" else "📄"
        with st.expander(f"{icon} [{n}] {c['source']} · {c['ref']} · skóre {c['score']:.2f}"):
            st.write(c["text"])
