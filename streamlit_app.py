import streamlit as st
import os
from graph import create_app

# Seite konfigurieren
st.set_page_config(page_title="KI-Moderations-System", page_icon="🛡️")

# Sicherstellen, dass die Keys vorhanden sind
if "OPENAI_API_KEY" not in os.environ:
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        if "TAVILY_API_KEY" in st.secrets:
            os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
    except KeyError:
        st.error("❌ OPENAI_API_KEY nicht in Streamlit Secrets gefunden!")
        st.info("""
        Bitte fügen Sie die Secret hinzu:
        1. Gehen Sie zu: **App Settings** (⚙️)
        2. Klicken Sie auf **Secrets**
        3. Fügen Sie ein: `OPENAI_API_KEY = "sk-..."`
        4. Speichern Sie
        """)
        st.stop()

# Initialisierung des Graphen
if "app" not in st.session_state:
    st.session_state.app = create_app()

st.title("🛡️ Multi-Agenten Moderations-System")
st.markdown("Analysieren Sie Kommentare mit KI-Agenten und menschlicher Freigabe.")

# Eingabe
user_input = st.text_area("Kommentar zur Prüfung:", placeholder="Geben Sie hier einen Kommentar ein...")

if st.button("Analyse starten") and user_input:
    # WICHTIG: Thread-ID für den Speicher (Human-in-the-loop)
    config = {"configurable": {"thread_id": "standard_user"}}
    inputs = {
        "originaler_kommentar": user_input,
        "relevante_richtlinien": "",
        "agenten_analyse": "",
        "moderations_status": "",
        "finale_begruendung": ""
    }

    st.session_state.current_input = user_input

    with st.status("Agenten arbeiten...", expanded=True) as status:
        try:
            # Den Graphen ausführen
            for event in st.session_state.app.stream(inputs, config=config):
                for node, values in event.items():
                    st.write(f"✅ **{node.capitalize()}** ist fertig.")
            status.update(label="Analyse abgeschlossen. Wartet auf Prüfung.", state="complete")
        except Exception as e:
            st.error(f"❌ Fehler: {str(e)}")
            st.error(f"Details: {type(e).__name__}")

# Human-in-the-Loop Bereich
config = {"configurable": {"thread_id": "standard_user"}}
snapshot = st.session_state.app.get_state(config)

if snapshot.next:
    st.divider()
    st.warning("⚠️ **Menschliche Entscheidung erforderlich**")

    # Werte aus dem Graphen abrufen
    daten = snapshot.values
    st.info(f"**KI-Begründung:** {daten.get('finale_begruendung', 'Keine Begründung vorhanden.')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Genehmigen"):
            st.session_state.app.update_state(config, {"moderations_status": "Genehmigt"})
            # Weiterlaufen lassen
            for event in st.session_state.app.stream(None, config=config):
                st.write(event)
            st.success("Kommentar wurde genehmigt!")

    with col2:
        if st.button("❌ Ablehnen"):
            st.session_state.app.update_state(config, {"moderations_status": "Abgelehnt"})
            for event in st.session_state.app.stream(None, config=config):
                st.write(event)
            st.error("Kommentar wurde abgelehnt.")
