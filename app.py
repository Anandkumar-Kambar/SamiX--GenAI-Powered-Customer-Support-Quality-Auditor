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
    from src.db.utils import get_db_engine, get_db
    from src.db.models import init_tables
    # Ensure src/api_client.py contains the SamiXClient class
    from src.api_client import SamiXClient 
    from src.ui.login_page import LoginPage
    from src.ui.dashboard import DashboardPage
    from src.ui.styles import inject_css
except ImportError as e:
    st.error(f"❌ Initialization Error: {e}")
    st.info("Check: Ensure every folder in 'src/' has an empty __init__.py file.")
    st.stop()

# 1. Page Configuration
st.set_page_config(
    page_title="SamiX · Quality Auditor", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session():
    """Initializes global session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = None

@st.cache_resource
def init_managers():
    """
    Initializes core engine connections once.
    BACKEND_URL should be set in Streamlit Cloud Secrets.
    """
    api_url = st.secrets.get("BACKEND_URL", "http://localhost:10000")
    engine = get_db_engine()
    
    return {
        "api": SamiXClient(base_url=api_url),
        "auth": AuthManager(engine),
        "db": get_db() # Standalone session for history/reports
    }

def main():
    # Initialize Database Tables & CSS
    init_tables() 
    inject_css()
    initialize_session()
    
    # Load Managers
    managers = init_managers()

    # Route: Login vs Dashboard
    if not st.session_state.authenticated:
        login_page = LoginPage(managers["auth"])
        login_page.render()
    else:
        # Render Sidebar Health Check
        with st.sidebar:
            st.markdown("### System Status")
            try:
                # Assuming SamiXClient has a health() method
                health = managers["api"].health()
                if health.get("status") == "healthy":
                    st.success("● AI Engine Online")
                else:
                    st.warning("● AI Engine Waking Up...")
            except Exception:
                st.error("● API Connection Offline")
            
            st.divider()
        
        # Main Dashboard View
        dashboard = DashboardPage(
            history_manager=managers["db"],
            kb_manager=managers["api"]
        )
        dashboard.render()

if __name__ == "__main__":
    main()
