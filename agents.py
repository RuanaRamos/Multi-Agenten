from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


def _get_client():
    api_key = os.environ.get("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY nicht gefunden! "
            "Konfigurieren Sie die Streamlit Secrets oder die .env-Datei."
        )
    return OpenAI(api_key=api_key)


def analysator_agent(state):
    """Analisa o sentimento e a intenção do comentário."""
    llm = _get_client()
    prompt = (
        f"Analysieren Sie den Kommentar: '{state['originaler_kommentar']}'. "
        "Klassifizieren Sie strikt in eine dieser Kategorien: [positiv, neutral, problematisch]. "
    )
    ia_anfrage = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    klassifizierung = ia_anfrage.choices[0].message.content.lower()

    status = "neutral"
    if "problematisch" in klassifizierung:
        status = "problematisch"
    elif "positiv" in klassifizierung:
        status = "positiv"

    return {"agenten_analyse": status}


def richtlinien_forscher_agent(state):
    """Sucht nach relevanten Richtlinien."""
    ergebnisse = "Richtlinie 1.1: Spam verboten. Richtlinie 2.2: Respekt ist obligatorisch."
    return {"relevante_richtlinien": ergebnisse}


def prüfer_agent(state):
    """Consolida a decisão final."""
    llm = _get_client()
    prompt = (
        f"Basierend auf der Analyse '{state['agenten_analyse']}' und den Richtlinien "
        f"'{state['relevante_richtlinien']}', moderieren Sie: "
        f"'{state['originaler_kommentar']}'. Antworten Sie auf Deutsch."
    )
    ia_anfrage = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "moderations_status": "Geprüft",
        "finale_begruendung": ia_anfrage.choices[0].message.content,
    }


def ausfuehrungs_agent(state):
    """Ação final."""
    print(f"\n--- AKTION AUSGEFÜHRT: {state.get('moderations_status', 'Unbekannt')} ---")
    return state
