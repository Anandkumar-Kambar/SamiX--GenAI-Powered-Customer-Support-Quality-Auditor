"""
SamiX - Quality Auditor Entry Point
Location: /app.py
"""
import os
import streamlit as st
from pathlib import Path
from src.auth.authenticator import AuthManager
from src.db import get_db
from src.api_client import SamiXClient
from src.ui.login_page import LoginPage
from src.ui.dashboard import DashboardPage
from src.ui.styles import inject_css

# 1. Page Config
st.set_page_config(
    page_title="SamiX · AI Auditor",
    page_icon="🛡️",
    layout="wide"
)

# 2. Initialize Persistent Clients
@st.cache_resource
def init_api():
    url = st.secrets.get("BACKEND_URL") or os.getenv("SAMIX_API_URL", "http://localhost:8000")
    return SamiXClient(base_url=url)

def main():
    inject_css()
    
    # Initialize session state
    if "api" not in st.session_state:
        st.session_state.api = init_api()
    if "auth" not in st.session_state:
        st.session_state.auth = AuthManager(get_db())
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # 3. Routing
    if not st.session_state.authenticated:
        LoginPage(st.session_state.auth).render()
    else:
        # Check if backend is awake (Render Free Tier health check)
        health = st.session_state.api.health()
        
        if health.get("status") == "offline":
            st.warning("📡 Connecting to SamiX Intelligence Cloud...")
            st.info("The backend is waking up. This usually takes 30 seconds on Render.")
            if st.button("Retry Connection"):
                st.rerun()
            return

        # Launch Dashboard
        DashboardPage(
            history_manager=get_db(),
            kb_manager=st.session_state.api
        ).render()

if __name__ == "__main__":
    main()
