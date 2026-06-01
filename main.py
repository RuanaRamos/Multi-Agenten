import os
import uuid
import urllib.parse

import streamlit as st

# ============================================================
# 1) Seiten-Konfiguration (muss als Erstes kommen)
# ============================================================
st.set_page_config(page_title="KI-Moderations-System", page_icon="🛡️")


# ============================================================
# 2) API-Schlüssel laden (VOR dem Import von graph/agents)
# ============================================================
def _load_api_keys():
    if os.environ.get("OPENAI_API_KEY"):
        return True
    try:
        if "OPENAI_API_KEY" in st.secrets:
            os.environ["OPENAI_API_KEY"] = str(st.secrets["OPENAI_API_KEY"]).strip()
            if "TAVILY_API_KEY" in st.secrets:
                os.environ["TAVILY_API_KEY"] = str(st.secrets["TAVILY_API_KEY"]).strip()
            return True
    except Exception:
        pass
    return False


if not _load_api_keys():
    st.error("❌ OPENAI_API_KEY nicht gefunden!")
    st.info(
        "Bitte konfigurieren Sie die Secrets:\n\n"
        "1. App-Settings (⚙️) öffnen\n"
        "2. Auf **Secrets** klicken\n"
        "3. Einfügen: `OPENAI_API_KEY = \"sk-...\"`\n"
        "4. Speichern"
    )
    st.stop()


# ============================================================
# 3) Graph importieren (nach dem Laden der Schlüssel)
# ============================================================
from graph import create_app  # noqa: E402


# ============================================================
# 4) Session-State initialisieren
# ============================================================
if "app" not in st.session_state:
    st.session_state.app = create_app()
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.awaiting_review = False

config = {"configurable": {"thread_id": st.session_state.thread_id}}


# ============================================================
# 5) UI
# ============================================================
st.title("🛡️ KI-Moderator mit Human-in-the-Loop")
st.markdown(
    "Dieses System nutzt eine **Multi-Agenten-Architektur** (via LangGraph), "
    "um Kommentare intelligent zu moderieren. "
    "**Besonderheit:** Bei kritischen Entscheidungen hält das System an und wartet auf Ihre Freigabe."
)

with st.sidebar:
    st.header("⚙️ Konfiguration")
    st.info(f"Thread-ID: {st.session_state.thread_id[:8]}...")
    if st.button("🔄 Sitzung zurücksetzen"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.awaiting_review = False
        st.session_state.app = create_app()
        st.rerun()

st.subheader("Neuen Kommentar prüfen")
user_input = st.text_area(
    "Kommentar hier eingeben:",
    placeholder="z.B.: Dieser Kurs ist schrecklich!",
)

if st.button("🚀 Analyse starten", type="primary") and user_input:
    inputs = {
        "originaler_kommentar": user_input,
        "relevante_richtlinien": "",
        "agenten_analyse": "",
        "moderations_status": "",
        "finale_begruendung": "",
    }

    with st.status("Agenten arbeiten...", expanded=True) as status:
        try:
            for event in st.session_state.app.stream(inputs, config=config):
                node_name = list(event.keys())[0]
                st.write(f"✅ Knoten **{node_name}** abgeschlossen.")
            status.update(label="Analyse beendet. Wartet auf Prüfung.", state="complete")
            st.session_state.awaiting_review = True
        except Exception as e:
            status.update(label="Fehler!", state="error")
            st.error(f"❌ Fehler: {type(e).__name__}: {e}")


# ============================================================
# 6) Human-in-the-Loop (nur am Breakpoint)
# ============================================================
try:
    snapshot = st.session_state.app.get_state(config)
except Exception:
    snapshot = None

if snapshot and snapshot.next and st.session_state.awaiting_review:
    st.divider()
    st.warning("⚠️ **Menschliche Überprüfung erforderlich**")

    daten = snapshot.values
    st.write(f"**Ursprünglicher Kommentar:** {daten.get('originaler_kommentar', '-')}")

    justificativa = st.text_area(
        "KI-Empfehlung (Begründung):",
        value=daten.get("finale_begruendung", ""),
        help="Sie können diesen Text vor der Veröffentlichung bearbeiten.",
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
                {"finale_begruendung": justificativa, "moderations_status": "Vom Menschen bearbeitet"},
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


# ============================================================
# 7) Workflow-Visualisierung
# ============================================================
st.divider()
st.subheader("📊 System-Workflow (Graph)")
try:
    mermaid_graph = st.session_state.app.get_graph().draw_mermaid()
    url = f"https://mermaid.ink/img/{urllib.parse.quote(mermaid_graph)}"
    st.image(url, use_container_width=True)
except Exception:
    st.info("Graph-Visualisierung wird geladen...")
