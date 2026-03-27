"""
SamiX Authentication Manager - Database Driven
Location: src/auth/authenticator.py
"""
from __future__ import annotations
import streamlit as st
import bcrypt
from sqlalchemy.orm import Session
# These imports are required for the methods below to work
from src.db.utils import get_user_by_email, create_user
from src.utils.validators import is_valid_email

class AuthManager:
    """
    Manages user credentials using SQLAlchemy.
    Synchronized with app.py and api_client.py session states.
    """

    def __init__(self, db_engine) -> None:
        """Initialize with the SQLAlchemy engine passed from app.py."""
        self.engine = db_engine

    def login(self, email: str, password: str) -> bool:
        """Verifies credentials and populates session state."""
        email = email.lower().strip()
        
        with Session(self.engine) as session:
            user = get_user_by_email(session, email)
            
            if user and self._check_password(password, user.hashed_password):
                # Update Session State (Matches app.py logic)
                st.session_state.authenticated = True
                st.session_state.user_data = {
                    "name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                    "id": user.id
                }
                # Mock token for api_client headers
                st.session_state.auth_token = f"sk-samix-{user.id}"
                return True
                
        st.session_state.authenticated = False
        return False

    def register(self, email: str, name: str, password: str, role: str = "agent") -> bool:
        """Registers a new user directly to the database."""
        email = email.lower().strip()
        if not is_valid_email(email):
            return False
            
        with Session(self.engine) as session:
            if get_user_by_email(session, email):
                return False  # User exists
            
            hashed_pw = self._hash_password(password)
            create_user(session, email, hashed_pw, name, role)
            return True

    def _hash_password(self, raw: str) -> str:
        """Generates a secure bcrypt hash."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(raw.encode('utf-8'), salt).decode('utf-8')

    def _check_password(self, raw: str, hashed: str) -> bool:
        """Validates a password against a hash."""
        try:
            return bcrypt.checkpw(raw.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def logout(self) -> None:
        """Clears all session keys and reboots the UI."""
        keys = ["authenticated", "user_data", "auth_token", "authentication_status"]
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    @property
    def current_user(self) -> dict:
        return st.session_state.get("user_data", {})
