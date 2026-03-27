"""
SamiX Admin Panel
Command center for supervisors to monitor all audits and system health.
"""
import streamlit as st
import pandas as pd
from src.ui.components import render_status_card

class AdminPanel:
    def __init__(self, history_manager, kb_manager):
        self.history = history_manager
        self.kb = kb_manager

    def render(self):
        """Renders the administrative overview."""
        st.markdown('<div class="samix-eyebrow">Administration</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="samix-title">Audit Management</h1>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 1. System Health Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_status_card("API Gateway", "Online", "success")
        with col2:
            render_status_card("Vector DB", "Connected", "success")
        with col3:
            render_status_card("LLM Queue", "Idle", "info")
        with col4:
            render_status_card("Database", "Healthy", "success")

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Main Admin Tabs
        tab_registry, tab_agents, tab_settings = st.tabs([
            "📋 Audit Registry", 
            "👥 Agent Performance", 
            "⚙️ System Settings"
        ])

        with tab_registry:
            self._render_audit_registry()
            
        with tab_agents:
            st.info("Agent ranking and trend analysis will appear here.")
            
        with tab_settings:
            self._render_settings()

    def _render_audit_registry(self):
        """Displays a searchable table of all past audits."""
        st.subheader("Global Audit Log")
        
        # Search & Filter bar
        search_col, filter_col = st.columns([2, 1])
        with search_col:
            st.text_input("Search by Agent or Filename", placeholder="Search...", label_visibility="collapsed")
        with filter_col:
            st.selectbox("Filter by Score", ["All Scores", "Critical (<50%)", "Good (>80%)"], label_visibility="collapsed")

        # Sample Data - In production, this pulls from self.history.get_all_audits()
        data = {
            "Date": ["2026-03-27", "2026-03-27", "2026-03-26"],
            "Agent": ["John Doe", "Jane Smith", "John Doe"],
            "Score": [85.5, 42.0, 91.2],
            "Status": ["Pass", "Critical Fail", "Pass"]
        }
        df = pd.DataFrame(data)
        
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn("Quality Score", min_value=0, max_value=100, format="%.1f%%"),
                "Status": st.column_config.TextColumn("Compliance Status")
            }
        )

    def _render_settings(self):
        """Basic admin controls for the AI thresholds."""
        st.subheader("AI Scoring Thresholds")
        with st.container(border=True):
            st.slider("Critical Failure Threshold", 0, 100, 50)
            st.slider("Pass Grade Threshold", 0, 100, 80)
            st.button("Update Thresholds", type="primary") 
