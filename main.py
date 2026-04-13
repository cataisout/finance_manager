
import os
from langchain_core.messages import HumanMessage
from graph.graph import build_graph
from agent.manager import Agent
from database.manager import DatabaseManager
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


conection_string = os.environ['CONNECTION_URI']
hf_token = os.environ['HF_TOKEN']

from auth import login_screen

# --- Configuração ---
st.set_page_config(
    page_title="Assistente Financeiro",
    layout="centered",
)

# --- LOGIN (bloqueia tudo antes) ---
login_screen()

# --- Inicialização ---
@st.cache_resource
def init_app():
    db_manager = DatabaseManager(connection_uri=conection_string)
    agent = Agent("Você é um assistente pessoal financeiro")
    graph = build_graph(agent=agent, db_manager=db_manager)
    return graph

graph = init_app()

# --- UI ---
st.title("💰 Assistente Financeiro")

# Logout
if st.button("Sair"):
    st.session_state.authenticated = False
    st.session_state.messages = []
    st.rerun()

# --- Estado da conversa ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Histórico ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input ---
user_input = st.chat_input("Digite sua mensagem...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            resp = graph.invoke({
                "messages": st.session_state.messages
            })

            answer = resp["messages"][-1].content
            st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })