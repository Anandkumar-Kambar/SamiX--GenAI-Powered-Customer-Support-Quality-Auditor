"""
SamiX Database Manager - Cloud Optimized
Handles SQLite persistence for both local dev and Render.com.
"""
from __future__ import annotations

import os
import json
import sqlite3
import logging
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional

# Setup logger
logger = logging.getLogger("samix.db")

class DBManager:
    """Thin SQLite data-access layer for SamiX runtime persistence."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        # 1. Environment-aware path selection
        if not db_path:
            # On Render, /tmp is usually the only writable directory for SQLite
            default_path = "/tmp/samix.db" if os.getenv("RENDER") else "samix.db"
            self.db_path = os.getenv("DB_PATH", default_path)
        else:
            self.db_path = db_path
            
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        """Initializes database schema if not already present."""
        # Find schema file relative to this script
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            logger.warning("schema.sql not found. Skipping table initialization.")
            return

        schema = schema_path.read_text(encoding="utf-8")
        try:
            with self._lock, self.connect() as conn:
                conn.executescript(schema)
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"DB Init Error: {e}")

    # --- Data Access Methods ---

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        with self._lock, self.connect() as conn:
            return conn.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        with self._lock, self.connect() as conn:
            return conn.execute(query, params).fetchall()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with self._lock, self.connect() as conn:
            cur = conn.execute(query, params)
            return int(cur.lastrowid or 0)

    # --- Business Logic ---

    def upsert_user(self, email: str, name: str, password_hash: str, role: str = "agent", is_active: bool = True) -> int:
        email = email.lower().strip()
        with self._lock, self.connect() as conn:
            row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if row:
                conn.execute(
                    "UPDATE users SET name=?, password_hash=?, role=?, is_active=?, updated_at=CURRENT_TIMESTAMP WHERE email=?",
                    (name, password_hash, role, int(is_active), email)
                )
                return int(row["id"])
            cur = conn.execute(
                "INSERT INTO users (email, name, password_hash, role, is_active) VALUES (?, ?, ?, ?, ?)",
                (email, name, password_hash, role, int(is_active))
            )
            return int(cur.lastrowid or 0)

    def get_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        row = self.fetch_one("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
        return dict(row) if row else None

    def save_audit_session(self, **kwargs) -> None:
        """Saves final audit results. Handles dict-to-json conversion for key_moments."""
        km = kwargs.get("key_moments", [])
        km_payload = km if isinstance(km, str) else json.dumps(km)
        
        query = """
            INSERT INTO audit_sessions (
                session_id, filename, agent_name, upload_time, mode, transcript_text,
                empathy_score, compliance_score, resolution_score, overall_score, 
                summary, violations, key_moments, token_count, cost_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET overall_score = excluded.overall_score
        """
        params = (
            kwargs['session_id'], kwargs['filename'], kwargs['agent_name'],
            kwargs['upload_time'], kwargs['mode'], kwargs['transcript_text'],
            kwargs['empathy_score'], kwargs['compliance_score'], kwargs['resolution_score'],
            kwargs['overall_score'], kwargs['summary'], kwargs['violations'],
            km_payload, kwargs.get('token_count', 0), kwargs.get('cost_usd', 0.0)
        )
        self.execute(query, params)

    def list_audit_rows(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.fetch_all("SELECT * FROM audit_sessions ORDER BY upload_time DESC")]

# --- Singleton Pattern ---
_db_singleton: Optional[DBManager] = None

def get_db() -> DBManager:
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = DBManager()
    return _db_singleton
