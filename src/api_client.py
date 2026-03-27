"""
SamiX API Client — Optimized for Streamlit + FastAPI (2026)
Handles Token-based Auth, Async Audits, and RAG operations.
"""
from __future__ import annotations

import os
import logging
import streamlit as st
from typing import Optional, Any, Dict

import httpx

logger = logging.getLogger("samix.client")

# Increased timeout for heavy LLM + Transcription workloads
_TIMEOUT = httpx.Timeout(150.0, connect=10.0)

class SamiXClient:
    """Thin HTTP wrapper around the SamiX FastAPI backend with Auth support."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        # Priority: Constructor -> Streamlit Secrets -> Env Var
        self.base_url = (
            base_url 
            or st.secrets.get("SAMIX_API_URL") 
            or os.getenv("SAMIX_API_URL", "")
        ).rstrip("/")
        
        # We initialize clients lazily or check availability
        self._client_instance: Optional[httpx.Client] = None
        self._async_client_instance: Optional[httpx.AsyncClient] = None

    @property
    def is_available(self) -> bool:
        """True if a backend URL is successfully configured."""
        return bool(self.base_url)

    def _get_auth_header(self) -> Dict[str, str]:
        """Retrieves the JWT token from Streamlit session state."""
        token = st.session_state.get("auth_token", "")
        return {"Authorization": f"Bearer {token}"} if token else {}

    def get_sync_client(self) -> httpx.Client:
        """Returns a persistent synchronous client."""
        if not self._client_instance:
            self._client_instance = httpx.Client(base_url=self.base_url, timeout=_TIMEOUT)
        return self._client_instance

    async def get_async_client(self) -> httpx.AsyncClient:
        """Returns a persistent asynchronous client."""
        if not self._async_client_instance:
            self._async_client_instance = httpx.AsyncClient(base_url=self.base_url, timeout=_TIMEOUT)
        return self._async_client_instance

    def health(self) -> dict[str, Any]:
        """GET /health — Check if the Render backend is awake."""
        if not self.is_available:
            return {"status": "local", "note": "Running in offline mode"}
        
        try:
            resp = self.get_sync_client().get("/health")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            return {"status": "error", "message": str(e)}

    async def run_audit(self, filename: str, file_bytes: bytes, agent_name: str = "Unknown") -> dict[str, Any]:
        """POST /audit — Sends audio, returns LLM scores & transcript."""
        if not self.is_available:
            raise RuntimeError("API Client not configured for remote audits.")

        client = await self.get_async_client()
        files = {"file": (filename, file_bytes, "audio/mpeg")}
        data = {"agent_name": agent_name}
        
        resp = await client.post(
            "/api/v1/audit", 
            files=files, 
            data=data,
            headers=self._get_auth_header()
        )
        resp.raise_for_status()
        return resp.json()

    async def query_rag(self, question: str, top_k: int = 5) -> dict[str, Any]:
        """POST /rag/query — Interfaces with Milvus via FastAPI."""
        client = await self.get_async_client()
        payload = {"question": question, "top_k": top_k}
        
        resp = await client.post(
            "/api/v1/rag/query", 
            json=payload,
            headers=self._get_auth_header()
        )
        resp.raise_for_status()
        return resp.json()

    async def upload_kb(self, filename: str, file_bytes: bytes) -> dict[str, Any]:
        """POST /kb/upload — Updates the policy vector database."""
        client = await self.get_async_client()
        files = {"file": (filename, file_bytes, "application/pdf")}
        
        resp = await client.post(
            "/api/v1/kb/upload", 
            files=files,
            headers=self._get_auth_header()
        )
        resp.raise_for_status()
        return resp.json()
