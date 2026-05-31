from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents import analysator_agent, richtlinien_forscher_agent, prüfer_agent, ausfuehrungs_agent

class AgentState(TypedDict, total=False):
    originaler_kommentar: str
    relevante_richtlinien: str
    agenten_analyse: str
    moderations_status: str
    finale_begruendung: str

def pruefe_forschungs_bedarf(state):
    if state["agenten_analyse"] == "problematisch":
        return "forscher"
    return "direkt_genehmigen"

def create_app():
    workflow = StateGraph(AgentState)

    workflow.add_node("analysator", analysator_agent)
    workflow.add_node("forscher", richtlinien_forscher_agent)
    workflow.add_node("pruefer", prüfer_agent)
    workflow.add_node("finalisierung", ausfuehrungs_agent)

    workflow.set_entry_point("analysator")

    workflow.add_conditional_edges(
        "analysator",
        pruefe_forschungs_bedarf,
        {"forscher": "forscher", "direkt_genehmigen": END}
    )

    workflow.add_edge("forscher", "pruefer")
    workflow.add_edge("pruefer", "finalisierung")
    workflow.add_edge("finalisierung", END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory, interrupt_before=["finalisierung"])