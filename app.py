"""
SamiX - Quality Auditor Entry Point
Status: Final Build - Streamlit Cloud to Render Production
"""
from __future__ import annotations
import os
import streamlit as st
from pathlib import Path
from PIL import Image

# Internal Imports
try:
    from src.auth.authenticator import AuthManager
    from src.db.utils import get_db_engine
    from src.db.models import init_tables
    from src.api_client import SamiXClient
    from src.ui.login_page import LoginPage
    from src.ui.dashboard import DashboardPage
    from src.ui.styles import inject_css
except ImportError as e:
    st.error(f"❌ Initialization Error: {e}")
    st.info("Ensure every folder in 'src/' has an empty __init__.py file.")
    st.stop()

st.set_page_config(page_title="SamiX · Quality Auditor", page_icon="🛡️", layout="wide")

def initialize_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = None

@st.cache_resource
def init_managers():
    # Pulls the Render URL from Streamlit Cloud Secrets
    api_url = st.secrets.get("BACKEND_URL") or "http://localhost:10000"
    return {
        "api": SamiXClient(base_url=api_url),
        "auth": AuthManager(get_db_engine())
    }

def main():
    init_tables() 
    inject_css()
    initialize_session()
    managers = init_managers()

    if not st.session_state.authenticated:
        LoginPage(managers["auth"]).render()
    else:
        # Render Sidebar with Health Check
        with st.sidebar:
            st.markdown("### SamiX Status")
            try:
                if managers["api"].health().get("status") == "healthy":
                    st.success("● API Engine Online")
                else:
                    st.warning("● API Waking Up...")
            except:
                st.error("● API Connection Failed")
        
        DashboardPage(
            history_manager=managers["auth"].db,
            kb_manager=managers["api"]
        ).render()

if __name__ == "__main__":
    main()
