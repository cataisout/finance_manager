import os
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def authenticate(username, password):
    return username == APP_USERNAME and password == APP_PASSWORD


def init_auth_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0

    if "blocked_until" not in st.session_state:
        st.session_state.blocked_until = 0


def login_screen():
    init_auth_state()

    now = time.time()

    # --- BLOQUEIO SILENCIOSO ---
    if now < st.session_state.blocked_until:
        st.title("🔐 Login")

        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            st.error("Credenciais inválidas")

        st.stop()

    # --- LOGIN NORMAL ---
    if not st.session_state.authenticated:
        st.title("🔐 Login")

        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.login_attempts = 0
                st.rerun()
            else:
                st.session_state.login_attempts += 1

                if st.session_state.login_attempts >= 3:
                    st.session_state.blocked_until = time.time() + (30 * 60)
                    st.session_state.login_attempts = 0

                st.error("Credenciais inválidas")

        st.stop()