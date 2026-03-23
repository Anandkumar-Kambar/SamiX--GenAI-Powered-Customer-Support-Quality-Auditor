"""
SamiX Login & Identity Gateway

This module implements a premium, dual-pane entry screen for the platform.
It features:
- Brand identity on the left with live (mock) KPI metrics.
- Secure authentication forms on the right for Sign In and Registration.
- Form-safe state management using Streamlit's native form containers.
"""
from __future__ import annotations

import streamlit as st
from pathlib import Path
from PIL import Image

from src.auth.authenticator import AuthManager


class LoginPage:
    """
    Renders a high-fidelity login experience.
    
    The layout is split into a branding section and an interactive auth section
    to create a professional, enterprise-grade first impression.
    """

    def __init__(self, auth: AuthManager) -> None:
        """ Initializes the login page with the centralized AuthManager. """
        self._auth = auth

    def render(self) -> None:
        """
        Entry point for rendering the gateway.
        Uses a two-column responsive layout for balanced visual weight.
        """
        # Distribute branding and forms in a 1:1 ratio with large spacing.
        col_brand, col_form = st.columns([1, 1], gap="large")

        with col_brand:
            self._render_brand()

        with col_form:
            self._render_form()

    # Render Logic (Private) 

    def _render_brand(self) -> None:
        """
        Visual Branding Section.
        Displays the SamiX logo, tagline, and real-time operational metrics
        to build user confidence before sign-in.
        """
        st.markdown("<br>", unsafe_allow_html=True)

        # Try to load custom logo from assets/images
        logo_path = Path("assets/images/logo.png")
        if logo_path.exists():
            try:
                logo = Image.open(logo_path)
                st.image(logo, width=120)
                st.markdown("<br>", unsafe_allow_html=True)
            except Exception as e:
                print(f"Could not load logo: {e}")
                self._render_default_logo()
        else:
            self._render_default_logo()

        # Professional Title
        st.markdown(
            '<div style="'
            'font-family:\'Inter\',sans-serif;'
            'font-size:2.5rem;'
            'font-weight:800;'
            'color:#0F172A;'
            'letter-spacing:-1px;'
            'line-height:1.1;'
            'margin-bottom:1rem;">'
            'Transform Your <span style="color:#152EAE;">Support Quality</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Subtitle
        st.markdown(
            '<div style="'
            'font-family:\'Inter\',sans-serif;'
            'font-size:1.1rem;'
            'color:#475569;'
            'line-height:1.6;'
            'margin-bottom:2.5rem;">'
            'SamiX AI provides real-time customer support quality assessment, compliance auditing, and intelligent business insights.<br><br>'
            '<span style="font-size:0.875rem;color:#94A3B8;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;">'
            'Powered by: Groq · Deepgram · Milvus · LangChain'
            '</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Live Operational Metrics 
        # Provide social proof and platform context.
        st.markdown(
            '<div style="'
            'display:grid;grid-template-columns:1fr 1fr;gap:1rem;'
            'margin-bottom:2rem;">'
        , unsafe_allow_html=True)
        
        c1, c2 = st.columns(2, gap="small")
        with c1:
            st.markdown(
                f'<div style="'
                f'background:#FFFFFF;'
                f'border:1px solid #E2E8F0;'
                f'border-radius:14px;'
                f'padding:1.5rem;'
                f'text-align:center;box-shadow:var(--shadow-sm);">'
                f'<div style="font-size:2.2rem;font-weight:800;color:#152EAE;font-family:\'Inter\',sans-serif;letter-spacing:-1px;">247</div>'
                f'<div style="font-size:0.75rem;color:#64748B;margin-top:0.5rem;font-family:\'Inter\',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Audits Today</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with c2:
            st.markdown(
                f'<div style="'
                f'background:#FFFFFF;'
                f'border:1px solid #E2E8F0;'
                f'border-radius:14px;'
                f'padding:1.5rem;'
                f'text-align:center;box-shadow:var(--shadow-sm);">'
                f'<div style="font-size:2.2rem;font-weight:800;color:#10B981;font-family:\'Inter\',sans-serif;letter-spacing:-1px;">73.4%</div>'
                f'<div style="font-size:0.75rem;color:#64748B;margin-top:0.5rem;font-family:\'Inter\',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Avg QA Score</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        c1, c2 = st.columns(2, gap="small")
        with c1:
            st.markdown(
                '<div style="'
                'background:linear-gradient(135deg,rgba(245,158,11,0.08),rgba(245,158,11,0.04));'
                'border:1px solid rgba(245,158,11,0.2);'
                'border-radius:12px;'
                'padding:1rem;'
                'text-align:center;">'
                '<div style="font-size:2rem;font-weight:700;color:#F59E0B;font-family:\'JetBrains Mono\',monospace;">18</div>'
                '<div style="font-size:0.75rem;color:#6B7280;margin-top:0.5rem;font-family:\'Inter\',sans-serif;font-weight:600;">Active Agents</div>'
                '</div>',
                unsafe_allow_html=True
            )
        
        with c2:
            st.markdown(
                '<div style="'
                'background:linear-gradient(135deg,rgba(239,68,68,0.08),rgba(239,68,68,0.04));'
                'border:1px solid rgba(239,68,68,0.2);'
                'border-radius:12px;'
                'padding:1rem;'
                'text-align:center;">'
                '<div style="font-size:2rem;font-weight:700;color:#EF4444;font-family:\'JetBrains Mono\',monospace;">38</div>'
                '<div style="font-size:0.75rem;color:#6B7280;margin-top:0.5rem;font-family:\'Inter\',sans-serif;font-weight:600;">Flagged Issues</div>'
                '</div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

    def _render_default_logo(self) -> None:
        """Fallback logo: Modern gradient badge when no custom logo found."""
        st.markdown(
            '<div style="'
            'display:flex;align-items:center;gap:0.75rem;margin-bottom:1.5rem;">'
            '<div style="'
            'width:52px;height:52px;'
            'background:linear-gradient(135deg,#152EAE,#2563EB);'
            'border-radius:14px;'
            'display:flex;align-items:center;justify-content:center;'
            'box-shadow:0 8px 16px rgba(21, 46, 174, 0.2);'
            '">'
            '<span style="font-size:1.6rem;color:#fff;font-weight:800;">S</span>'
            '</div>'
            '<div style="font-family:\'Inter\',sans-serif;">'
            '<div style="font-size:1.5rem;font-weight:800;color:#0F172A;margin:0;letter-spacing:-0.5px;">Shopeers <span style="color:#2563EB;">AI</span></div>'
            '<div style="font-size:0.65rem;color:#64748B;font-weight:700;letter-spacing:0.1em;margin:0;text-transform:uppercase;">Analytics Platform</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    def _render_form(self) -> None:
        """
        Interactive Authentication Section.
        Toggles between Sign In and Registration workflows.
        """
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Welcome Header
        st.markdown(
            '<div style="'
            'font-family:\'Inter\',sans-serif;'
            'font-size:2rem;'
            'font-weight:800;'
            'color:#0F172A;'
            'letter-spacing:-0.5px;'
            'margin-bottom:0.5rem;">'
            'Welcome'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="'
            'font-family:\'Inter\',sans-serif;'
            'font-size:0.95rem;'
            'color:#64748B;'
            'margin-bottom:2.5rem;'
            'font-weight:500;">'
            'Sign in to access your analytics dashboard'
            '</div>',
            unsafe_allow_html=True,
        )

        # Tab styling with modern appearance
        tab_login, tab_register = st.tabs(["Sign In", "Register"])

        with tab_login:
            # Wrap in form to allow 'Enter' key submission.
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input(
                    "Email Address",
                    placeholder="name@company.com",
                    label_visibility="collapsed",
                    key="login_email"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    label_visibility="collapsed",
                    key="login_password"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button(
                    "🔓 Sign In",
                    width="stretch",
                    help="Sign in with your email and password"
                )

                if submit:
                    if not email or not password:
                        st.error("Please provide both email and password.", icon="⚠")
                    else:
                        success = self._auth.login(email, password)
                        if success:
                            st.rerun()
                        else:
                            st.error("Incorrect email or password.", icon="🔒")

            if self._auth.is_pending():
                st.info(
                    "💡 Enter your credentials to access the platform.",
                    icon="ℹ️"
                )

        with tab_register:
            # Registration requires confirmation and field validation.
            with st.form("register_form", clear_on_submit=True):
                name = st.text_input(
                    "Full Name",
                    placeholder="Jane Doe",
                    label_visibility="collapsed",
                    key="register_name"
                )
                email = st.text_input(
                    "Email Address",
                    placeholder="name@company.com",
                    label_visibility="collapsed",
                    key="register_email"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    label_visibility="collapsed",
                    key="register_password"
                )
                confirm_pwd = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="••••••••",
                    label_visibility="collapsed",
                    key="register_confirm"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button(
                    "✨ Create Account",
                    use_container_width=True,
                    help="Create a new account"
                )

                if submit:
                    if not name or not email or not password:
                        st.error("Please fill in all the fields.", icon="⚠")
                    elif password != confirm_pwd:
                        st.error("Passwords do not match.", icon="⚠")
                    else:
                        success = self._auth.register(email, name, password)
                        if success:
                            st.success(
                                f"✅ Account created! Please sign in with your credentials.",
                                icon=None
                            )
                        else:
                            st.error("An account with this email already exists.", icon="⚠")
