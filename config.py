"""
SamiX Configuration Module

Centralized configuration management for environment settings,
API keys, and application-wide constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class Config:
    """Application configuration container."""
    
    # ========== ENVIRONMENT ==========
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # ========== PATHS ==========
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    KB_DIR = DATA_DIR / "kb"
    AUTH_DIR = DATA_DIR / "auth"
    HISTORY_DIR = DATA_DIR / "history"
    UPLOADS_DIR = DATA_DIR / "uploads"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # Ensure directories exist
    for directory in [DATA_DIR, KB_DIR, AUTH_DIR, HISTORY_DIR, UPLOADS_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # ========== DATABASE ==========
    MILVUS_DB_PATH = str(PROJECT_ROOT / "milvus_lite.db")
    USERS_YAML = str(AUTH_DIR / "users.yaml")
    
    # ========== API KEYS ==========
    # Primary: Read from Streamlit secrets (production via Cloud)
    # Fallback: Read from .env or environment variables (local development)
    @staticmethod
    def get_groq_api_key():
        try:
            return st.secrets["groq"]["api_key"]
        except:
            return os.getenv("GROQ_API_KEY", "NOT_CONFIGURED")
    
    @staticmethod
    def get_deepgram_api_key():
        try:
            return st.secrets["deepgram"]["api_key"]
        except:
            return os.getenv("DEEPGRAM_API_KEY", "NOT_CONFIGURED")
    
    @staticmethod
    def get_email_config():
        try:
            return {
                "smtp_host": st.secrets["email"]["smtp_host"],
                "smtp_port": st.secrets["email"]["smtp_port"],
                "sender_address": st.secrets["email"]["sender_address"],
                "sender_password": st.secrets["email"]["sender_password"],
            }
        except:
            return {
                "smtp_host": os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
                "sender_address": os.getenv("EMAIL_SENDER_ADDRESS", ""),
                "sender_password": os.getenv("EMAIL_SENDER_PASSWORD", ""),
            }
    
    # ========== LOGGING ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "samix.log")
    
    # ========== STREAMLIT SETTINGS ==========
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    
    # ========== RAG CONFIGURATION ==========
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100
    TOP_K = 5
    EMBED_MODEL = "BAAI/bge-small-en-v1.5"
    
    # ========== STT CONFIGURATION ==========
    AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"}
    TEXT_EXTS = {".csv", ".json", ".txt"}
    CONF_THRESHOLD = 0.70
    
    @staticmethod
    def validate_configuration():
        """Validates that all critical configurations are properly set."""
        errors = []
        
        groq_key = Config.get_groq_api_key()
        if not groq_key or groq_key == "NOT_CONFIGURED" or "your_" in groq_key.lower():
            errors.append("⚠ GROQ_API_KEY not properly configured")
        
        # Deepgram is optional (fallback to Whisper available)
        deepgram_key = Config.get_deepgram_api_key()
        if "your_" in deepgram_key.lower():
            print("ℹ DEEPGRAM_API_KEY not configured - will use local Whisper as fallback")
        
        return errors
    
    @classmethod
    def print_status(cls):
        """Prints current configuration status for debugging."""
        print("\n" + "=" * 60)
        print("SamiX Configuration Status")
        print("=" * 60)
        print(f"Environment: {cls.APP_ENV}")
        print(f"Debug Mode: {cls.DEBUG}")
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"Milvus DB: {cls.MILVUS_DB_PATH}")
        print(f"Users File: {cls.USERS_YAML}")
        
        groq_key = Config.get_groq_api_key()
        print(f"Groq API: {'✓ Configured' if 'gsk_' in groq_key else '✗ Not configured'}")
        
        deepgram_key = Config.get_deepgram_api_key()
        print(f"Deepgram API: {'✓ Configured' if 'your_' not in deepgram_key else 'ℹ Using Whisper fallback'}")
        
        print("=" * 60 + "\n")

# Validate on import
errors = Config.validate_configuration()
if errors:
    for error in errors:
        print(error)
