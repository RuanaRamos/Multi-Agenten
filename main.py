import streamlit as st
import uuid
import urllib.parse
import os

# Seitenkonfiguration
st.set_page_config(page_title="KI-Moderations-System", page_icon="🛡️")

# Carregar as chaves de API antes de importar o graph
if "OPENAI_API_KEY" not in os.environ:
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        if "TAVILY_API_KEY" in st.secrets:
            os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
    except KeyError:
        st.error("❌ OPENAI_API_KEY nicht in Streamlit Secrets gefunden!")
        st.info("Bitte gehen Sie zu: App Settings → Secrets und fügen Sie hinzu:\nOPENAI_API_KEY = 'sk-...'")
        st.stop()

from graph import create_app

st.title("🛡️ KI-Moderator mit Human-in-the-Loop")
st.markdown("""
Dieses System nutzt eine **Multi-Agenten-Architektur** (via LangGraph), um Kommentare intelligent zu moderieren. 
**Besonderheit:** Bei kritischen Entscheidungen hält das System an und wartet auf Ihre Freigabe.
""")

# Initialisierung von Graph und Session State
if "app" not in st.session_state:
    st.session_state.app = create_app()
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.awaiting_review = False

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Seitenleiste (Sidebar)
with st.sidebar:
    st.header("⚙️ Konfiguration")
    st.info(f"Thread-ID: {st.session_state.thread_id}")
    if st.button("Sitzung zurücksetzen"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.awaiting_review = False
        st.rerun()

# Eingabebereich
st.subheader("Neuen Kommentar prüfen")
user_input = st.text_area("Kommentar hier eingeben:", placeholder="z.B.: Dieser Kurs ist schrecklich! Besuchen Sie virus.com")

if st.button("Analyse starten") and user_input:
    inputs = {
        "originaler_kommentar": user_input,
        "relevante_richtlinien": "",
        "agenten_analyse": "",
        "moderations_status": "",
        "finale_begruendung": ""
    }
    
    with st.status("Agenten arbeiten...", expanded=True) as status:
        for event in st.session_state.app.stream(inputs, config=config):
            # Zeigt an, welcher Agent gerade aktiv ist
            node_name = list(event.keys())[0]
            st.write(f"✅ Knoten **{node_name}** abgeschlossen.")
        status.update(label="Analyse beendet. Wartet auf Prüfung.", state="complete")
    
    st.session_state.awaiting_review = True

# Human-in-the-Loop Bereich (Erscheint nur am Breakpoint)
snapshot = st.session_state.app.get_state(config)

if snapshot.next and st.session_state.awaiting_review:
    st.divider()
    st.warning("⚠️ **Menschliche Überprüfung erforderlich**")
    
    daten = snapshot.values
    st.write(f"**Ursprünglicher Kommentar:** {daten.get('originaler_kommentar')}")
    
    # KI-Vorschlag bearbeitbar machen
    justificativa = st.text_area(
        "KI-Empfehlung (Begründung):", 
        value=daten.get('finale_begruendung', ''),
        help="Sie können diesen Text vor der Veröffentlichung bearbeiten."
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Genehmigen"):
            st.session_state.app.update_state(config, {"moderations_status": "Genehmigt"})
            for event in st.session_state.app.stream(None, config=config):
                st.write(event)
            st.success("Erfolgreich genehmigt!")
            st.session_state.awaiting_review = False

    with col2:
        if st.button("📝 Bearbeiten & Senden"):
            st.session_state.app.update_state(
                config, 
                {"finale_begruendung": justificativa, "moderations_status": "Vom Menschen bearbeitet"}
            )
            for event in st.session_state.app.stream(None, config=config):
                st.write(event)
            st.info("Bearbeitete Version gesendet.")
            st.session_state.awaiting_review = False

    with col3:
        if st.button("❌ Ablehnen"):
            st.session_state.app.update_state(config, {"moderations_status": "Abgelehnt"})
            st.error("Moderation abgebrochen.")
            st.session_state.awaiting_review = False

# Workflow-Visualisierung
st.divider()
st.subheader("📊 System-Workflow (Graph)")
try:
    mermaid_graph = st.session_state.app.get_graph().draw_mermaid()
    url = f"https://mermaid.ink/img/{urllib.parse.quote(mermaid_graph)}"
    st.image(url, use_column_width=True)
except Exception:
    st.info("Graph-Visualisierung wird geladen...")
