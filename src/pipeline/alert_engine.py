"""
SamiX Alert & Notification Engine - Backend Optimized

1. Removed Streamlit dependencies (prevents crashes on Render).
2. Uses standard logging for alerts.
3. Environment-variable based SMTP configuration.
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
from typing import Optional

# Setup logger for Render/FastAPI visibility
logger = logging.getLogger("samix.alerts")

def _safe_console(message: str) -> None:
    """Safe logging for production environments."""
    logger.info(message)

class AlertEngine:
    """Dispatches system alerts and SMTP notifications via Backend."""

    SCORE_THRESHOLD: float = 60.0

    def __init__(self) -> None:
        self._email_cfg = self._load_email_cfg()

    def _load_email_cfg(self) -> Optional[dict]:
        """Loads SMTP config from environment variables (Render Dashboard)."""
        try:
            # We check OS environ first for Render compatibility
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
        """Analyzes results and triggers notifications."""
        triggered: list[str] = []
        
        # Handle different types of violation inputs safely
        if isinstance(violations, int):
            violation_count = violations
        elif isinstance(violations, list):
            violation_count = len(violations)
        else:
            violation_count = 0

        # 1. AUTO-FAIL Alert
        if auto_fail:
            msg = f"🚨 AUTO-FAIL - {filename} | Agent: {agent_name} | Reason: {auto_fail_reason}"
            logger.warning(msg)
            if recipient_email:
                await self._email(recipient_email, "SamiX AUTO-FAIL Alert", msg)
            triggered.append(msg)

        # 2. LOW SCORE Alert
        if final_score < self.SCORE_THRESHOLD:
            msg = (
                f"⚠️ LOW SCORE - {filename} | Agent: {agent_name} | "
                f"Score: {final_score:.0f}/100"
            )
            logger.info(msg)
            if recipient_email:
                await self._email(recipient_email, "SamiX Low Score Alert", msg)
            triggered.append(msg)

        # 3. CRITICAL VIOLATION Alert
        if violation_count > 2:
            msg = (
                f"🔴 CRITICAL VIOLATIONS - {filename} | Agent: {agent_name} | "
                f"{violation_count} violations detected"
            )
            logger.error(msg)
            if recipient_email:
                await self._email(recipient_email, "SamiX Critical Violation", msg)
            triggered.append(msg)

        return triggered

    async def _email(self, recipient: str, subject: str, body: str) -> bool:
        """Async wrapper for SMTP delivery."""
        if not self._email_cfg or not recipient:
            self._mock_log(recipient, subject, body)
            return False
        return await asyncio.to_thread(self._sync_email, recipient, subject, body)

    def _sync_email(self, recipient: str, subject: str, body: str) -> bool:
        """Synchronous SMTP logic."""
        try:
            cfg = self._email_cfg
            msg = MIMEMultipart("alternative")
            msg["From"] = cfg["sender_address"]
            msg["To"] = recipient
            msg["Subject"] = f"[SamiX Alert] {subject}"

            html_body = f"""
            <html><body style="font-family:sans-serif; background:#f4f4f4; padding:20px;">
            <div style="background:white; padding:20px; border-radius:10px; border-left:5px solid #60A5FA;">
