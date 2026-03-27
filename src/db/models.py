 """
SamiX Database Models
Location: src/db/models.py
"""
from __future__ import annotations
import bcrypt
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="agent") # 'admin' or 'agent'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditSession(Base):
    __tablename__ = "audit_sessions"
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    score = Column(Float)
    sentiment = Column(String)
    transcript = Column(Text)
    analysis = Column(Text) # Detailed LLM feedback
    duration = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

def init_tables():
    """
    1. Creates all database tables.
    2. Seeds an initial admin user if the table is empty.
    """
    # Import inside function to avoid circular import with utils.py
    from src.db.utils import get_db_engine, get_db
    from sqlalchemy.orm import Session
    
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    
    # Seed Admin User
    db: Session = get_db()
    try:
        admin_email = "admin@samix.ai"
        admin_exists = db.query(User).filter(User.email == admin_email).first()
        
        if not admin_exists:
            # Match bcrypt hashing used in AuthManager
            raw_password = "samix2026"
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')
            
            first_admin = User(
                email=admin_email,
                full_name="System Admin",
                hashed_password=hashed_pw,
                role="admin"
            )
            db.add(first_admin)
            db.commit()
            print(f"✅ Database Seeding: Created admin account ({admin_email})")
    except Exception as e:
        print(f"⚠️ Seeding Warning: {e}")
    finally:
        db.close()
