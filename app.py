import streamlit as st
import os
from graph import create_app

# Seite konfigurieren
st.set_page_config(page_title="KI-Moderations-System", page_icon="🛡️")

# Sicherstellen, dass die Keys vorhanden sind
if "OPENAI_API_KEY" not in os.environ:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
    else:
        st.error("❌ API-Keys nicht in Streamlit Secrets gefunden!")

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
    inputs = {"originaler_kommentar": user_input}
    
    st.session_state.current_input = user_input
    
    with st.status("Agenten arbeiten...", expanded=True) as status:
        try:
            # Den Graphen ausführen
            for event in st.session_state.app.stream(inputs, config=config):
                for node, values in event.items():
                    st.write(f"✅ **{node.capitalize()}** ist fertig.")
            status.update(label="Analyse abgeschlossen. Wartet auf Prüfung.", state="complete")
        except Exception as e:
            st.error(f"Fehler während der Agenten-Kommunikation: {e}")
            st.info("Hinweis: Prüfen Sie, ob Ihr OpenAI-Key korrekt in den Secrets hinterlegt ist.")

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
