import uuid
import urllib.parse
from graph import create_app

app = create_app()
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

eingabe = {"originaler_kommentar": "Dieser Kurs ist schrecklich! Besuchen Sie virus.com"}

print(f"--- SITZUNG GESTARTET: {thread_id} ---")

for event in app.stream(eingabe, config=config):
    print(event)

snapshot = app.get_state(config)

if snapshot.next:
    daten = snapshot.values
    print(f"\n🤖 KI-EMPFEHLUNG: {daten.get('finale_begruendung')}")
    
    auswahl = input("\n1. Genehmigen | 2. Bearbeiten | 3. Ablehnen: ")
    
    if auswahl == "1":
        for event in app.stream(None, config=config): print(event)
    elif auswahl == "2":
        nova = input("Nova justificativa: ")
        app.update_state(config, {"finale_begruendung": nova, "moderations_status": "Edited"})
        for event in app.stream(None, config=config): print(event)
    elif auswahl == "3":
        print("Cancelado.")

# Link do Diagrama
mermaid_graph = app.get_graph().draw_mermaid()
print(f"\n🎨 Diagramm: https://mermaid.ink/img/{urllib.parse.quote(mermaid_graph)}")