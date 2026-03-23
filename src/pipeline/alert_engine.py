"""
SamiX Alert & Notification Engine

This module handles the distribution of alerts when quality thresholds are breached.
It supports:
1. Real-time UI notifications via Streamlit's `st.toast`.
2. Automated email alerts via SMTP (with a fallback mock-logger for local development).
"""
from __future__ import annotations

import asyncio
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import streamlit as st


class AlertEngine:
    """
    Evaluates audit results and fires alerts based on predefined thresholds.
    
    Alerts are triggered for:
    - Overall scores below a minimum threshold.
    - Presence of 'Critical' violations.
    - Automatic failure conditions.
    """

    # Minimum acceptable quality score (out of 100).
    SCORE_THRESHOLD: float = 60.0

    def __init__(self) -> None:
        """ Initialize the engine and discover email configuration from secrets. """
        self._email_cfg = self._load_email_cfg()

    def _load_email_cfg(self) -> Optional[dict]:
        """ Attempts to load SMTP credentials from streamlit secrets. """
        try:
            cfg = st.secrets.get("email", {})
            # Ensure the config isn't just the default placeholder.
            if cfg and "REPLACE" not in cfg.get("sender_address", "REPLACE"):
                return dict(cfg)
        except Exception:
            pass
        return None

    # Public API 

    async def check_and_fire(
        self,
        filename: str,
        agent_name: str,
        final_score: float,
        violations: int,
        auto_fail: bool,
        auto_fail_reason: str,
        recipient_email: str = "",
    ) -> list[str]:
        """
        Analyzes a completed audit and triggers notifications asynchronously.
        Returns a list of strings describing the alerts that were fired.
        Input validation: violations can be int (count) or list (detailed violations).
        """
        triggered: list[str] = []
        
        # Input validation: Handle both int and list violations
        violation_count = violations if isinstance(violations, int) else len(violations) if violations else 0

        # 1. Handle Auto-Failures (e.g., severe compliance breach).
        if auto_fail:
            msg = f"AUTO-FAIL — {filename} · {agent_name} · Reason: {auto_fail_reason}"
            self._toast(msg, icon="🚨")
            if recipient_email:
                await self._email(recipient_email, "SamiX AUTO-FAIL Alert", msg)
            triggered.append(msg)

        # 2. Handle Low Quality Scores.
        if final_score < self.SCORE_THRESHOLD:
            msg = (
                f"LOW SCORE — {filename} · {agent_name} · "
                f"Score: {final_score:.0f}/100 (threshold {self.SCORE_THRESHOLD:.0f})"
            )
            self._toast(msg, icon="⚠️")
            if recipient_email:
                await self._email(recipient_email, "SamiX Low Score Alert", msg)
            triggered.append(msg)

        # 3. Handle Critical Violations (violation count trigger).
        if violation_count > 2:  # More than 2 violations is critical
            msg = (
                f"CRITICAL VIOLATIONS — {filename} · {agent_name} · "
                f"{violation_count} violations detected"
            )
            self._toast(msg, icon="🔴")
            if recipient_email:
                await self._email(recipient_email, "SamiX Critical Violation", msg)
            triggered.append(msg)

        return triggered

    async def send_custom(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> bool:
        """
        Sends a manual notification asynchronously.
        Provides real-time feedback in the UI.
        """
        success = await self._email(to, subject, body)
        if success:
            st.toast(f"📧 Email sent to {to}", icon="✅")
        else:
            st.toast(f"📧 Email queued (mock) for {to}", icon="📬")
        return success

    # Internal Utilities 

    @staticmethod
    def _toast(message: str, icon: str = "⚠️") -> None:
        """ Triggers a non-blocking UI popup. """
        st.toast(message, icon=icon)

    async def _email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> bool:
        """
        Dispatches an email via SMTP if configured (using asyncio.to_thread).
        """
        if not self._email_cfg or not recipient:
            self._mock_log(recipient, subject, body)
            return False

        return await asyncio.to_thread(self._sync_email, recipient, subject, body)

    def _sync_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> bool:
        """ Synchronous backend logic for email dispatch. """
        try:
            # Extract SMTP details from configuration.
            host     = self._email_cfg["smtp_host"]
            port     = int(self._email_cfg.get("smtp_port", 587))
            sender   = self._email_cfg["sender_address"]
            password = self._email_cfg["sender_password"]

            # Construct a rich-text (HTML) email message.
            msg = MIMEMultipart("alternative")
            msg["From"]    = sender
            msg["To"]      = recipient
            msg["Subject"] = f"[SamiX] {subject}"

            html_body = f"""
            <html><body style="font-family:monospace;background:#0F172A;color:#E2E8F0;padding:24px;">
            <h2 style="color:#8B5CF6;">SamiX · Quality Auditor Alert</h2>
            <p>{body.replace(chr(10),'<br>')}</p>
            <hr style="border-color:#334155;"/>
            <p style="color:#64748B;font-size:12px;">
              Sent by SamiX · {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </p>
            </body></html>
            """
            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Establish a secure connection and send.
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(sender, password)
                server.sendmail(sender, recipient, msg.as_string())
            return True

        except Exception as exc:
            # Fallback to mock log if SMTP fails.
            self._mock_log(recipient, subject, f"{body}\n\n[SMTP Error: {exc}]")
            return False

    @staticmethod
    def _mock_log(to: str, subject: str, body: str) -> None:
        """ Logs a formatted 'email' block to the server console for testing. """
        print(
            f"\n{'─'*60}\n"
            f"[SamiX MOCK EMAIL]\n"
            f"To:      {to or '(no recipient)'}\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}\n"
            f"{'─'*60}\n"
        )
