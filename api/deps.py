"""
SamiX API — Dependency Injection
Optimized for Render.com 
"""
from __future__ import annotations

import os
import logging
import sys
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

# 1. Improved Path Handling: Ensure 'src' is findable regardless of how the app is started
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load .env from project root if it exists (local dev)
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger("samix.api")

def _ensure_env() -> None:
    """
    Ensures critical keys exist. 
    On Render, these are pulled directly from the Dashboard Environment Variables.
    """
    critical_keys = ["GROQ_API_KEY", "DEEPGRAM_API_KEY", "HF_TOKEN"]
    missing = [k for k in critical_keys if not os.getenv(k)]
    
    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}. Some features may fail.")

@lru_cache(maxsize=1)
def get_groq_client():
    """Singleton GroqClient."""
    _ensure_env()
    from src.pipeline.groq_client import GroqClient
    return GroqClient()

@lru_cache(maxsize=1)
def get_stt_processor():
    """
    Singleton STTProcessor.
    Ensures it defaults to Deepgram API to avoid loading local Whisper models.
    """
    _ensure_env()
    from src.pipeline.stt_processor import STTProcessor
    # We pass use_api=True if your class supports it, 
    # otherwise ensure your STTProcessor logic checks for DEEPGRAM_API_KEY
    return STTProcessor()

@lru_cache(maxsize=1)
def get_kb_manager():
    """
    Singleton KBManager.
    CRITICAL: Ensure your KBManager class in src/utils/kb_manager.py 
    uses HuggingFaceInferenceAPI if HF_TOKEN is present.
    """
    _ensure_env()
    from src.utils.kb_manager import KBManager
    return KBManager()

@lru_cache(maxsize=1)
def get_audio_processor():
    """Singleton AudioProcessor."""
    from src.utils.audio_processor import AudioProcessor
    return AudioProcessor()

@lru_cache(maxsize=1)
def get_cost_tracker():
    """Singleton CostTracker."""
    from src.utils.cost_tracker import CostTracker
    return CostTracker()

@lru_cache(maxsize=1)
def get_alert_engine():
    """Singleton AlertEngine."""
    from src.pipeline.alert_engine import AlertEngine
    return AlertEngine()
