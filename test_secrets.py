import os
import streamlit as st

st.title("🔍 Debug: Verificar Secrets")

# Verificar se as chaves estão carregadas
if "OPENAI_API_KEY" in os.environ:
    key_preview = os.environ["OPENAI_API_KEY"][:10] + "***"
    st.success(f"✅ OPENAI_API_KEY carregada: {key_preview}")
else:
    st.error("❌ OPENAI_API_KEY não encontrada em os.environ")

if "OPENAI_API_KEY" in st.secrets:
    key_preview = st.secrets["OPENAI_API_KEY"][:10] + "***"
    st.success(f"✅ OPENAI_API_KEY em st.secrets: {key_preview}")
else:
    st.error("❌ OPENAI_API_KEY não encontrada em st.secrets")

st.divider()
st.info("Para usar a app, configure as secrets no Streamlit Cloud:")
st.code("""
OPENAI_API_KEY = "sk-..."
TAVILY_API_KEY = "tvly-..."
""")
