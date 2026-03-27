"""
SamiX AI Inference Engine (Groq Client) - Cloud Optimized
- Client Mode: Routes analysis requests to Render Backend (Streamlit safe).
- Server Mode: Executes dual-call Llama-3 pipeline on Render.
"""
from __future__ import annotations

import json
import os
import requests
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Optional, Any, List

# Use logging for backend compatibility
logger = logging.getLogger("samix.groq")

from src.db import get_db
from src.storage import FileStorage
from src.utils.history_manager import (
    AuditScores, TranscriptTurn, WrongTurn,
    EngineAResult, EngineBClaim, EngineBResult, EngineCResult
)

@dataclass
class SummaryResult:
    customer_query: str
    sub_queries: list[str]
    query_category: str
    customer_expectation: str
    phases: dict
    key_moments: list[str]

@dataclass
class ScoringResult:
    scores: AuditScores
    engine_a: EngineAResult
    engine_b: EngineBResult
    engine_c: EngineCResult
    violations: list[dict]
    wrong_turns: list[WrongTurn]
    auto_fail: bool
    auto_fail_reason: str
    token_count: int

# --- AI System Prompt ---
_SCORING_SYSTEM_PROMPT = """
You are SamiX, a senior quality auditor. Return ONLY valid JSON.
Scoring weights: empathy 20%, professionalism 15%, compliance 25%, resolution 20%, communication 5%, integrity 15%.
"""

class GroqClient:
    MODEL: str = "llama-3.3-70b-versatile"

    def __init__(self, api_base: Optional[str] = None) -> None:
        # Detect Environment
        self.api_url = api_base or os.environ.get("BACKEND_URL")
        self.is_client = self.api_url is not None
        
        if self.is_client:
            logger.info(f"Groq Client Mode: Routing to {self.api_url}")
            self._async_client = None
        else:
            logger.info("Groq Server Mode: Initializing AsyncGroq")
            self._async_client = self._build_async_client()
            self._db = get_db()
            self._storage = FileStorage()

    def _build_async_client(self) -> Optional[object]:
        try:
            from groq import AsyncGroq
            key = os.environ.get("GROQ_API_KEY", "")
            return AsyncGroq(api_key=key) if key else None
        except Exception:
            return None

    @property
    def is_live(self) -> bool:
        if self.is_client: return True
        return self._async_client is not None

    async def summarise(self, transcript_text: str, session_id: Optional[str] = None) -> SummaryResult:
        if self.is_client:
            return await self._proxy_request("summarise", {"transcript": transcript_text})
        return await self._real_summarise(transcript_text, session_id or str(uuid.uuid4())[:8])

    async def score(self, transcript_text: str, summary: SummaryResult, rag_context: str = "", session_id: Optional[str] = None) -> ScoringResult:
        if self.is_client:
            return await self._proxy_request("score", {
                "transcript": transcript_text, 
                "summary": summary.__dict__ if hasattr(summary, '__dict__') else summary, 
                "rag": rag_context
            })
        return await self._real_score(transcript_text, summary, rag_context, session_id or str(uuid.uuid4())[:8])

    async def _proxy_request(self, endpoint: str, payload: dict):
        """Frontend Proxy to Render."""
        try:
            resp = requests.post(f"{self.api_url}/{endpoint}", json=payload, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                if endpoint == "summarise": return SummaryResult(**data)
                return data # Scoring results are usually handled as raw dicts in the UI
            return self._mock_summary() if endpoint == "summarise" else self._mock_scoring()
        except Exception as e:
            logger.error(f"Proxy failed: {e}")
            return self._mock_summary() if endpoint == "summarise" else self._mock_scoring()

    # --- Server Implementations ---

    async def _real_summarise(self, transcript_text: str, session_id: str) -> SummaryResult:
        prompt = f"Summarize this transcript as JSON:\n{transcript_text}"
        try:
            started = time.perf_counter()
            resp = await self._async_client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
            return SummaryResult(
                customer_query=data.get("customer_query", ""),
                sub_queries=data.get("sub_queries", []),
                query_category=data.get("query_category", "General"),
                customer_expectation=data.get("customer_expectation", ""),
                phases=data.get("phases", {}),
                key_moments=data.get("key_moments", [])
            )
        except Exception as e:
            logger.error(f"Summarize failed: {e}")
            return self._mock_summary()

    async def _real_score(self, transcript_text: str, summary: SummaryResult, rag_context: str, session_id: str) -> ScoringResult:
        user_msg = f"Transcript: {transcript_text}\nSummary: {summary}\nRAG: {rag_context}"
        try:
            started = time.perf_counter()
            resp = await self._async_client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": _SCORING_SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.05,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
            return self._parse_scoring_response(data, resp.usage.total_tokens)
        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return self._mock_scoring()

    def _parse_scoring_response(self, d: dict, tokens: int) -> ScoringResult:
        # Reusing your existing normalization logic
        cust_sent = d.get("customer_sentiment_by_turn", [5.0])
        agent_turn = d.get("agent_score_by_turn", [5.0])
        
        scores = AuditScores(
            empathy=float(d.get("empathy", 5.0)),
            professionalism=float(d.get("professionalism", 5.0)),
            compliance=float(d.get("compliance", 5.0)),
            resolution=float(d.get("resolution", 5.0)),
            communication=float(d.get("communication", 5.0)),
            integrity=float(d.get("integrity", 5.0)),
            opening=float(d.get("opening_score", 5.0)),
            middle=float(d.get("middle_score", 5.0)),
            closing=float(d.get("closing_score", 5.0)),
            phase_bonus=float(d.get("phase_bonus", 0.0)),
            final_score=float(d.get("final_score", 50.0)),
            verdict=d.get("verdict", "Neutral"),
            customer_sentiment=cust_sent,
            customer_overall=sum(cust_sent)/len(cust_sent),
            agent_by_turn=agent_turn
        )

        return ScoringResult(
            scores=scores,
            engine_a=EngineAResult(**d.get("engine_a", {"primary_query_answered":True, "sub_queries_addressed":True, "is_fake_close":False, "resolution_state":"Closed"})),
            engine_b=EngineBResult(claims=[]),
            engine_c=EngineCResult(customer_frustrated_but_ok=False, agent_rushed=False, resolution_confirmed_by_customer=True),
            violations=d.get("violations", []),
            wrong_turns=[],
            auto_fail=d.get("auto_fail", False),
            auto_fail_reason=d.get("auto_fail_reason", ""),
            token_count=tokens
        )

    def _mock_summary(self) -> SummaryResult:
        return SummaryResult("Mock Query", [], "General", "None", {}, [])

    def _mock_scoring(self) -> ScoringResult:
        # Returns a basic safe object if API fails
        return ScoringResult(None, None, None, None, [], [], False, "", 0)
