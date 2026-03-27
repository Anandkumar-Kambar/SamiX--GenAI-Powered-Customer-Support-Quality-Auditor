"""
SamiX - Agent Workspace
Location: src/ui/agent_panel.py
Status: FIX #3 - Async API Integration & Gauge UI
"""
from __future__ import annotations

import asyncio
import streamlit as st
from datetime import datetime

class AgentPanel:
    def __init__(self, history_manager, kb_manager):
        self.db = history_manager
        self.api = kb_manager # This is the SamiXClient

    def render(self):
        st.header("🎙️ Agent Audit Workspace")
        st.info("Upload customer interaction audio for AI-powered quality scoring.")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Upload Call")
            uploaded_file = st.file_uploader("Select Call Recording (MP3/WAV)", type=["mp3", "wav"])
            agent_name = st.text_input("Agent Name", value=st.session_state.user_data.get("name", ""))
            
            if st.button("Start AI Audit", use_container_width=True, type="primary"):
                if uploaded_file and agent_name:
                    self._handle_audit(uploaded_file, agent_name)
                else:
                    st.warning("Please provide both a file and an agent name.")

        with col2:
            st.subheader("Recent Audits")
            # This pulls from the local SQLite history we set up in Fix #1
            history = self.db.query("SELECT id, agent_name, score, timestamp FROM audit_sessions ORDER BY timestamp DESC LIMIT 5")
            if history:
                for item in history:
                    st.write(f"**{item[1]}** - Score: `{item[2]}%` ({item[3][:10]})")
            else:
                st.caption("No recent audits found.")

    def _handle_audit(self, file, agent_name):
        """Wrapper to run the async API call in Streamlit's sync environment."""
        with st.status("🚀 Processing Audit...", expanded=True) as status:
            try:
                st.write("📤 Uploading to Render Backend...")
                file_bytes = file.read()
                
                # Run the async call from api_client.py
                result = asyncio.run(self.api.run_audit(
                    filename=file.name,
                    file_bytes=file_bytes,
                    agent_name=agent_name
                ))

                st.write("✅ Audit Complete!")
                status.update(label="Audit Finished Successfully!", state="complete")
                
                # Show results in an expander
                with st.expander("📊 View Audit Results", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Score", f"{result.get('score', 0)}%")
                    c2.metric("Sentiment", result.get("sentiment", "Neutral"))
                    c3.metric("Duration", f"{result.get('duration', 0)}s")
                    
                    st.markdown("### 📝 Transcript")
                    st.write(result.get("transcript", "No transcript available."))

            except Exception as e:
                st.error(f"Audit Failed: {str(e)}")
                status.update(label="Error occurred", state="error")
