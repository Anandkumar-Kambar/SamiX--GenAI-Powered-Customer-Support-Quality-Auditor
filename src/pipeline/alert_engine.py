"""
SamiX Alert & Notification Engine - Cloud Optimized
- Client Mode: Collects alerts for UI display (Streamlit safe).
- Server Mode: Dispatches SMTP notifications (Render.com optimized).
"""
from __future__ import annotations

import asyncio
import smtplib
import ssl
import os
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Any

# Setup logger for backend visibility
logger = logging.getLogger("samix.alerts")

class AlertEngine:
    """Dispatches system alerts and SMTP notifications."""

    SCORE_THRESHOLD: float = 60.0

    def __init__(self, api_base: Optional[str] = None) -> None:
        # 1. Detect Environment
        # If BACKEND_URL exists, we are the Streamlit Client.
        self.api_url = api_base or os.environ.get("BACKEND_URL")
        self.is_client = self.api_url is not None
        
        # 2. Only load SMTP config if we are the actual Backend Server
        self._email_cfg = self._load_email_cfg() if not self.is_client else None

    def _load_email_cfg(self) -> Optional[dict]:
        """Loads SMTP config from environment variables (Render Dashboard)."""
        try:
            sender = os.getenv("SMTP_SENDER")
            password = os.getenv("SMTP_PASSWORD")
            host = os.getenv("SMTP_HOST")
            port = os.getenv("SMTP_PORT", "587")

            if all([sender, password, host]):
                return {
                    "sender_address": sender,
                    "sender_password": password,
                    "smtp_host": host,
                    "smtp_port": port
                }
        except Exception as e:
            logger.error(f"Failed to load email config: {e}")
        return None

    async def check_and_fire(
        self,
        filename: str,
        agent_name: str,
        final_score: float,
        violations: Any,
        auto_fail: bool,
        auto_fail_reason: str,
        recipient_email: str = "",
    ) -> list[str]:
        """
        Analyzes results and returns a list of alert messages.
        If on Server, it also triggers the SMTP email process.
        """
        triggered: list[str] = []
        
        # Handle violation input safely (list or int)
        if isinstance(violations, (int, float)):
            violation_count = violations
        elif isinstance(violations, list):
            violation_count = len(violations)
        else:
            violation_count = 0

        # 1. AUTO-FAIL Alert
        if auto_fail:
            msg = f"🚨 AUTO-FAIL - {filename} | Agent: {agent_name} | Reason: {auto_fail_reason}"
            triggered.append(msg)
            if not self.is_client and recipient_email:
                await self._email(recipient_email, "SamiX AUTO-FAIL Alert", msg)

        # 2. LOW SCORE Alert
        if final_score < self.SCORE_THRESHOLD:
            msg = f"⚠️ LOW SCORE - {filename} | Agent: {agent_name} | Score: {final_score:.0f}/100"
            triggered.append(msg)
            if not self.is_client and recipient_email:
                await self._email(recipient_email, "SamiX Low Score Alert", msg)

        # 3. CRITICAL VIOLATION Alert
        if violation_count > 2:
            msg = f"🔴 CRITICAL VIOLATIONS - {filename} | Agent: {agent_name} | {violation_count} violations"
            triggered.append(msg)
            if not self.is_client and recipient_email:
                await self._email(recipient_email, "SamiX Critical Violation", msg)

        # Server-side logging
        if not self.is_client:
            for m in triggered:
                logger.info(f"Alert Triggered: {m}")

        return triggered

    async def _email(self, recipient: str, subject: str, body: str) -> bool:
        """Async wrapper for SMTP delivery."""
        if not self._email_cfg or not recipient:
            return False
        return await asyncio.to_thread(self._sync_email, recipient, subject, body)

    def _sync_email(self, recipient: str, subject: str, body: str) -> bool:
        """Synchronous SMTP logic (Runs in thread)."""
        try:
            cfg = self._email_cfg
            msg = MIMEMultipart("alternative")
            msg["From"] = cfg["sender_address"]
            msg["To"] = recipient
            msg["Subject"] = f"[SamiX Alert] {subject}"
            
            # Simple text part
            msg.attach(MIMEText(body, "plain"))
            
            # HTML part
            html_content = f"<h3>SamiX Quality Alert</h3><p>{body}</p>"
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"])) as server:
                server.starttls()
                server.login(cfg["sender_address"], cfg["sender_password"])
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"SMTP delivery failed: {e}")
            return False
