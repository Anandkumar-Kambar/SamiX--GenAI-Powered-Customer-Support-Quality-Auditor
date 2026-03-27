"""
SamiX Dashboard UI
The central traffic controller for SamiX.
Handles sidebar navigation and role-based access.
Location: src/ui/dashboard.py
"""
from __future__ import annotations
import streamlit as st

# Internal Imports - Ensure these files exist in src/ui/
try:
    from src.ui.styles import inject_css
    from src.ui.admin_panel import AdminPanel
    from src.ui.agent_panel import AgentPanel
    from src.ui.reports_page import ReportsPage
    from src.ui.components import render_page_hero
except ImportError:
    # Fallback to prevent app crash during development
    pass

class DashboardPage:
    def __init__(self, history_manager, kb_manager):
        self.history = history_manager
        self.kb = kb_manager

    def render(self) -> None:
        """Main rendering loop with role-based routing."""
        # 1. Apply global styling
        try:
            inject_css()
        except:
            pass

        # 2. Extract session data
        user = st.session_state.get("user_data", {"name": "User", "role": "agent"})
        role = user.get("role", "agent")

        # 3. Sidebar Configuration
        with st.sidebar:
            st.markdown(f"### 🛡️ SamiX Workspace")
            st.caption(f"Logged in as **{user.get('name')}** ({role.capitalize()})")
            st.divider()

            if role == "admin":
                nav_options = ["Overview", "Audit Management", "Policy Knowledge Base", "Compliance Reports"]
            else:
                nav_options = ["Agent Audit", "Performance History"]

            selection = st.radio("Navigation", nav_options)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("Sign Out", use_container_width=True, type="secondary"):
                # Clear all session data
                for key in ["authenticated", "user_data", "auth_token"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        # 4. Route to specific views
        if selection == "Overview":
            self._render_overview(user.get("name"))
        
        elif selection == "Audit Management":
            # Pass managers to the Admin Panel
            AdminPanel(self.history, self.kb).render()
            
        elif selection == "Compliance Reports":
            ReportsPage(self.history).render()
            
        elif selection == "Agent Audit":
            AgentPanel(self.history, self.kb).render()
            
        elif selection == "Performance History":
            st.subheader("Your Audit History")
            st.info("Individual performance tracking coming soon.")
            
        elif selection == "Policy Knowledge Base":
            st.subheader("Knowledge Base Management")
            st.info("RAG/Milvus management tools coming in the next milestone.")

    def _render_overview(self, name: str) -> None:
        """A high-level greeting page for Admins."""
        try:
            render_page_hero(
                eyebrow="Welcome Back",
                title=f"Hello, {name}",
                subtitle="Here is your quality assurance overview for the last 24 hours.",
                stats=[
                    ("Total Audits", "1,284", "+12%"),
                    ("Avg Score", "82/100", "Steady"),
                    ("Critical Breaches", "3", "-20%")
                ]
            )
        except:
            # Simple fallback if component fails
            st.title(f"Hello, {name}")
            st.write("QA overview for the last 24 hours.")
        
        st.markdown("---")
        st.markdown("### Recent Activity")
        st.info("Connect your Render API endpoint to populate real-time activity feeds.")
