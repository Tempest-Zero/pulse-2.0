"""
User Model
SQLAlchemy ORM model for users.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """
    User model for multi-user support with authentication.
    
    Attributes:
        id: Primary key
        email: Unique email for login
        username: Display name
        password_hash: Hashed password (not exposed in API)
        is_active: Whether account is active
        created_at: When the user was created
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (excludes password_hash for security)."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
