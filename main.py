import streamlit as st
import uuid
import urllib.parse
from graph import create_app

# Configuração da página
st.set_page_config(page_title="Multi-Agent Moderator", page_icon="🤖")

st.title("🤖 Moderador de IA com Supervisão Humana")
st.markdown("""
Esta interface demonstra um sistema de múltiplos agentes orquestrados pelo **LangGraph**.
O fluxo analisa o comentário e **para** para sua revisão caso detecte algo problemático.
""")

# Inicializa o Grafo e a Sessão
if "app" not in st.session_state:
    st.session_state.app = create_app()
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.awaiting_review = False

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Sidebar com informações técnicas
with st.sidebar:
    st.header("Configurações")
    st.info(f"ID da Sessão: {st.session_state.thread_id}")
    if st.button("Limpar Histórico"):
        st.session_state.messages = []
        st.session_state.awaiting_review = False
        st.rerun()

# Campo de entrada de dados
user_input = st.text_area("Digite o comentário para análise:", placeholder="Ex: Esse curso é horrível! Acesse virus.com")

if st.button("Analisar Comentário") and user_input:
    inputs = {"originaler_kommentar": user_input}
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Executa o grafo até o breakpoint
    with st.status("Agentes trabalhando...", expanded=True) as status:
        for event in st.session_state.app.stream(inputs, config=config):
            st.write(event)
        status.update(label="Análise concluída. Aguardando revisão.", state="complete")
    
    st.session_state.awaiting_review = True

# Área de Revisão Humana (Aparece apenas quando o grafo para)
snapshot = st.session_state.app.get_state(config)
if snapshot.next and st.session_state.awaiting_review:
    st.warning("⚠️ **Intervenção Humana Necessária**")
    dados = snapshot.values
    
    st.subheader("Sugestão da IA:")
    justificativa = st.text_area("Justificativa do Agente Revisor:", value=daten.get('finale_begruendung', ''))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Aprovar"):
            st.session_state.app.update_state(config, {"moderations_status": "Aprovado"})
            for event in st.session_state.app.stream(None, config=config):
                st.write(event)
            st.success("Ação executada com sucesso!")
            st.session_state.awaiting_review = False

    with col2:
        if st.button("📝 Salvar Edição"):
            st.session_state.app.update_state(config, {"finale_begruendung": justificativa, "moderations_status": "Editado pelo Humano"})
            for event in st.session_state.app.stream(None, config=config):
                st.write(event)
            st.success("Justificativa editada e enviada!")
            st.session_state.awaiting_review = False

    with col3:
        if st.button("❌ Rejeitar"):
            st.session_state.app.update_state(config, {"moderations_status": "Rejeitado pelo Humano"})
            st.error("Ação cancelada.")
            st.session_state.awaiting_review = False

# Exibição do Diagrama Mermaid
st.divider()
try:
    mermaid_graph = st.session_state.app.get_graph().draw_mermaid()
    url = f"https://mermaid.ink/img/{urllib.parse.quote(mermaid_graph)}"
    st.image(url, caption="Fluxo de Trabalho dos Agentes")
except Exception as e:
    st.error(f"Erro ao gerar diagrama: {e}")
