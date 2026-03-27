"""
SamiX Database Utilities
Thread Safety Enabled
"""
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

def get_db_path():
    """Determines the persistent path for the SQLite database."""
    # Check for Render persistent disk first
    if os.path.exists("/data"):
        return "/data/samix.db"
    
    # Local fallback logic
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        
    return os.path.join(data_dir, "samix.db")

def get_db_engine():
    """
    Creates the engine with thread safety for Streamlit.
    """
    db_path = f"sqlite:///{get_db_path()}"
    return create_engine(
        db_path, 
        # CRITICAL: Allows multi-threaded Streamlit to access SQLite without crashing
        connect_args={"check_same_thread": False} 
    )

def get_db() -> Session:
    """
    Helper to get a database session.
    """
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def sqlite_healthcheck(session) -> dict:
    """Returns database metadata for the DB Admin Panel."""
    try:
        db_file = get_db_path()
        size_kb = os.path.getsize(db_file) // 1024 if os.path.exists(db_file) else 0
        
        # Get table names directly from sqlite
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [{"name": row[0]} for row in cursor.fetchall()]
        conn.close()

        return {
            "status": "healthy",
            "path": db_file,
            "size_kb": size_kb,
            "tables": tables
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
