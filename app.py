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
    st.info("Check: 1. Requirements installed? 2. __init__.py files in src folders?")
    st.stop()

# 1. Page Configuration
st.set_page_config(
    page_title="SamiX · Quality Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def initialize_session():
    """Sets default session states to prevent KeyErrors."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = None
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None

@st.cache_resource
def init_managers():
    """
    Initializes core engines. 
    On Streamlit Cloud, it prioritizes st.secrets['BACKEND_URL'].
    """
    # Priority: Streamlit Cloud Secrets -> Local Environment -> Default Localhost
    api_url = st.secrets.get("BACKEND_URL") or os.getenv("BACKEND_URL") or "http://localhost:10000"
    
    return {
        "api": SamiXClient(base_url=api_url),
        "auth": AuthManager(get_db_engine())
    }

def render_sidebar_header(api: SamiXClient):
    """Renders the branding and performs a non-blocking backend health check."""
    with st.sidebar:
        # Logo handling
        logo_path = Path("assets/images/logo.png")
        if logo_path.exists():
            st.image(Image.open(logo_path), width=100)
        else:
            st.markdown('<div style="width:48px;height:48px;background:linear-gradient(135deg,#6366F1,#4F46E5);border-radius:12px;margin:0 auto 1rem auto;display:flex;align-items:center;justify-content:center;"><span style="color:#fff;font-weight:800;font-size:1.2rem;">S</span></div>', unsafe_allow_html=True)
        
        st.markdown('<div style="text-align:center;color:#F8FAFC;font-weight:800;font-size:1.3rem;">SamiX</div>', unsafe_allow_html=True)
        st.divider()

        # Health Check UI
        st.markdown('<div style="font-size:.65rem;font-weight:700;color:#64748B;">SERVER STATUS</div>', unsafe_allow_html=True)
        try:
            status = api.health()
            if status.get("status") == "healthy":
                st.success("● API Engine Online")
            else:
                st.warning("● API Waking Up...")
        except Exception:
            st.error("● API Connection Failed")

def main():
    # 1. System Initializations
    init_tables() 
    inject_css()
    initialize_session()
    
    # 2. Setup Managers
    managers = init_managers()

    # 3. Routing Logic
    if not st.session_state.authenticated:
        # Show Login Page if not authenticated
        LoginPage(managers["auth"]).render()
    else:
        # Show Sidebar Branding
        render_sidebar_header(managers["api"])
        
        # Launch Dashboard (Handles Admin vs Agent views internally)
        dashboard = DashboardPage(
            history_manager=managers["auth"].db,
            kb_manager=managers["api"]
        )
        dashboard.render()

if __name__ == "__main__":
    main()
