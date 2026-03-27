"""
SamiX Database Utilities
"""
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_path():
    """
    Determines the best path for the SQLite database.
    On Render, /data is a common persistent mount point.
    """
    # Check if a persistent 'data' directory exists (common in Docker/Render mounts)
    if os.path.exists("/data"):
        return "/data/samix.db"
    
    # Local fallback: ensure a 'data' folder exists in the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    return os.path.join(data_dir, "samix.db")

def get_db_engine():
    db_path = f"sqlite:///{get_db_path()}"
    return create_engine(db_path, connect_args={"check_same_thread": False})

def sqlite_healthcheck(session) -> dict:
    """Returns database metadata for the DB Admin Panel."""
    try:
        db_file = get_db_path()
        size_kb = os.path.getsize(db_file) // 1024 if os.path.exists(db_file) else 0
        
        # Get table names
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
