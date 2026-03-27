"""
SamiX Authentication Gateway
Handles brand storytelling and secure access with session persistence.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image
import streamlit as st

from src.auth.authenticator import AuthManager


class LoginPage:
    def __init__(self, auth: AuthManager) -> None:
        self._auth = auth
        # Initialize session state keys if they don't exist
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_data" not in st.session_state:
            st.session_state.user_data = None

    def render(self) -> None:
        """Main render loop for the login screen."""
        # Use a centered container for better mobile responsiveness
        left, right = st.columns([1.2, 0.8], gap="large")
        
        with left:
            self._render_brand()
        
        with right:
            self._render_form()

    def _render_brand(self) -> None:
        """Renders the left-side marketing and tech-stack overview."""
        logo_path = Path("assets/images/logo.png")
        st.markdown('<div class="samix-hero">', unsafe_allow_html=True)

        if logo_path.exists():
            try:
                st.image(Image.open(logo_path), width=100)
            except Exception:
                self._fallback_logo()
        else:
            self._fallback_logo()

        st.markdown(
            """
            <div class="samix-eyebrow">AI Quality Operations</div>
            <h1 class="samix-title">Review support calls with speed and grounded policy checks.</h1>
            <p class="samix-subtitle">
              SamiX orchestrates Groq-powered LLMs and Milvus RAG to automate 
              compliance audits for high-volume support teams.
            </p>
            
            <div class="samix-kpi-grid">
              <div class="samix-kpi-card">
                <div class="samix-kpi-label">LLM Engine</div>
                <div class="samix-kpi-value">Groq Llama 3</div>
              </div>
              <div class="samix-kpi-card">
                <div class="samix-kpi-label">Vector DB</div>
                <div class="samix-kpi-value">Milvus Lite</div>
              </div>
              <div class="samix-kpi-card">
                <div class="samix-kpi-label">Audio STT</div>
                <div class="samix-kpi-value">Deepgram</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    def _fallback_logo(self) -> None:
        """SaaS-style CSS logo if image asset is missing."""
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:2rem;">
              <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#6366F1,#4F46E5);display:flex;align-items:center;justify-content:center;box-shadow:0 10px 15px -3px rgba(79,70,229,0.4);">
                <span style="color:#fff;font-size:1.2rem;font-weight:800;">S</span>
              </div>
              <div>
                <div style="font-size:1.4rem;font-weight:800;color:#F1F5F9;letter-spacing:-0.03em;">SamiX</div>
                <div style="font-size:0.7rem;color:#6366F1;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;">Intelligence</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _render_form(self) -> None:
        """Renders the login/register toggle and handles form submission."""
        st.markdown(
            """
            <div class="samix-shell">
              <h2 style="color:white; margin-bottom:0.5rem;">Access Workspace</h2>
              <p style="color:#94A3B8; font-size:0.9rem;">Sign in to review audits or manage policies.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="admin@samix.ai")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Enter Dashboard", use_container_width=True)

                if submit:
                    user = self._auth.login(email, password)
                    if user:
                        # SET SESSION STATE
                        st.session_state.authenticated = True
                        st.session_state.user_data = user  # Assuming user object has 'role', 'name'
                        st.success("Authentication successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

            if self._auth.is_pending():
                st.info("💡 Protip: Use `admin@samix.ai` / `admin` for initial setup.")

        with tab_register:
            with st.form("register_form"):
                name = st.text_input("Full Name")
                reg_email = st.text_input("Work Email")
                reg_pass = st.text_input("Password", type="password")
                reg_conf = st.text_input("Confirm Password", type="password")
                
                # Role selection for demonstration (usually handled via invite or admin)
                role = st.selectbox("Role", ["Agent", "Supervisor"])
                
                reg_submit = st.form_submit_button("Create Account", use_container_width=True)

                if reg_submit:
                    if reg_pass != reg_conf:
                        st.error("Passwords do not match.")
                    elif self._auth.register(reg_email, name, reg_pass, role=role.lower()):
                        st.success("Account created! You can now sign in.")
                    else:
                        st.error("Registration failed. Email may already be in use.")
