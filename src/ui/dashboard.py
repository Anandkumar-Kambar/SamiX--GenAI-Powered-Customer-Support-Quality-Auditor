from __future__ import annotations

import streamlit as st
from src.ui.styles import inject_css
from src.ui.admin_panel import AdminPanel
from src.ui.agent_panel import AgentPanel
from src.ui.reports_page import ReportsPage
from src.ui.components import render_page_hero

class DashboardPage:
    def __init__(self, history_manager, kb_manager):
        self.history = history_manager
        self.kb = kb_manager

    def render(self) -> None:
        """
        The central traffic controller for SamiX.
        Handles sidebar navigation and role-based access.
        """
        # 1. Apply global styling
        inject_css()

        # 2. Extract session data (set during login)
        user = st.session_state.get("user_data", {"name": "Guest", "role": "agent"})
        role = user.get("role", "agent")

        # 3. Sidebar Configuration
        with st.sidebar:
            st.markdown(f"### 🛡️ SamiX Workspace")
            st.caption(f"Logged in as **{user.get('name')}** ({role.capitalize()})")
            st.divider()

            if role == "admin":
                nav_options = ["Overview", "Audit Management", "Policy Knowledge Base", "Compliance Reports"]
                nav_icons = ["📊", "🔍", "📚", "📈"]
            else:
                nav_options = ["Agent Audit", "Performance History"]
                nav_icons = ["🎧", "📜"]

            selection = st.radio("Navigation", nav_options, label_visibility="collapsed")
            
            st.spacer(20) # Push logout to bottom
            if st.button("Sign Out", use_container_width=True, type="secondary"):
                st.session_state.authenticated = False
                st.rerun()

        # 4. Route to specific views
        if selection == "Overview":
            self._render_overview(user.get("name"))
        
        elif selection == "Audit Management":
            AdminPanel(self.history, self.kb).render()
            
        elif selection == "Compliance Reports":
            ReportsPage(self.history).render()
            
        elif selection == "Agent Audit":
            AgentPanel(self.history, self.kb).render()
            
        elif selection == "Policy Knowledge Base":
            # This would link to your RAG/Milvus management page
            st.info("Knowledge Base Management coming in the next milestone.")

    def _render_overview(self, name: str) -> None:
        """A high-level greeting page for Admins."""
        render_page_hero(
            eyebrow="Welcome Back",
            title=f"Hello, {name}",
            subtitle="Here is your quality assurance overview for the last 24 hours.",
            stats=[
                ("Total Audits", "1,284", "+12% vs yesterday"),
                ("Avg Score", "82/100", "Steady"),
                ("Critical Breaches", "3", "-20% improvement")
            ]
        )
        
        st.markdown("### Recent Activity")
        # Placeholder for a activity stream or small chart
        st.info("Connect your Render API endpoint to populate real-time activity feeds.")
