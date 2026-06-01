from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def analysator_agent(state):
    """Analisa o sentimento e a intenção do comentário."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY nicht gefunden! "
            "Bitte konfigurieren Sie die Umgebungsvariable oder Streamlit Secrets."
        )

    llm = OpenAI(api_key=api_key)
    prompt = (
        f"Analysieren Sie den Kommentar: '{state['originaler_kommentar']}'. "
        "Klassifizieren Sie strikt in eine dieser Kategorien: [positiv, neutral, problematisch]. "
    )
    ia_anfrage = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    klassifizierung = ia_anfrage.choices[0].message.content.lower()

    status = "neutral"
    if "problematisch" in klassifizierung: status = "problematisch"
    elif "positiv" in klassifizierung: status = "positiv"

    return {"agenten_analyse": status}

def richtlinien_forscher_agent(state):
    """Sucht nach relevanten Richtlinien."""
    ergebnisse = "Richtlinie 1.1: Spam verboten. Richtlinie 2.2: Respekt ist obligatorisch."
    return {"relevante_richtlinien": ergebnisse}

def prüfer_agent(state):
    """Consolida a decisão final."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY nicht gefunden! "
            "Bitte konfigurieren Sie die Umgebungsvariable oder Streamlit Secrets."
        )

    llm = OpenAI(api_key=api_key)
    prompt = (
        f"Basierend auf der Analyse '{state['agenten_analyse']}' und den Richtlinien '{state['relevante_richtlinien']}', "
        f"moderieren Sie: '{state['originaler_kommentar']}'. Responda em alemão."
    )
    ia_anfrage = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"moderations_status": "Geprüft", "finale_begruendung": ia_anfrage.choices[0].message.content}

def ausfuehrungs_agent(state):
    """Ação final."""
    print(f"\n--- AKTION AUSGEFÜHRT: {state['moderations_status']} ---")
    return state