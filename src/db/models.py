"""
SamiX Database Models
"""
import hashlib
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from src.db.utils import get_db_engine, get_db

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="agent") # 'admin' or 'agent'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditSession(Base):
    __tablename__ = "audit_sessions"
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String)
    score = Column(Float)
    sentiment = Column(String)
    transcript = Column(Text)
    duration = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

def init_tables():
    """
    1. Creates all database tables.
    2. Automatically creates an admin user if the table is empty.
    """
    engine = get_db_engine()
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session to check for initial admin
    db = get_db()
    try:
        # Check if any admin exists
        admin_exists = db.query(User).filter(User.username == "admin").first()
        
        if not admin_exists:
            # Default Credentials: admin / samix2026
            hashed_pw = hashlib.sha256("samix2026".encode()).hexdigest()
            first_admin = User(
                username="admin",
                password_hash=hashed_pw,
                role="admin"
            )
            db.add(first_admin)
            db.commit()
            print("✅ Database Seeding: Admin user 'admin' created successfully.")
    except Exception as e:
        print(f"⚠️ Database Seeding Warning: {e}")
    finally:
        db.close()
