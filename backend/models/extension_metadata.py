"""
Extension Metadata Models
Database models for browser extension data, consent tracking, and browsing sessions.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from models.base import Base


class BrowsingSession(Base):
    """
    Aggregated browsing session data from the extension.
    Sessions are hourly aggregates of user activity.
    """
    __tablename__ = "browsing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # Optional: link to user account

    # Temporal data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    hour_key = Column(String(20), nullable=False)  # e.g., "2025-01-15T14"
    duration_minutes = Column(Integer, default=60)

    # Category distribution (minutes spent)
    work_time = Column(Integer, default=0)
    leisure_time = Column(Integer, default=0)
    social_time = Column(Integer, default=0)
    neutral_time = Column(Integer, default=0)

    # Behavioral metrics
    tab_switches = Column(Integer, default=0)
    window_focus_changes = Column(Integer, default=0)
    avg_focus_duration_minutes = Column(Float, default=0.0)
    distraction_rate_per_hour = Column(Float, default=0.0)
    unique_domains = Column(Integer, default=0)

    # Metadata
    event_count = Column(Integer, default=0)
    client_timestamp = Column(DateTime(timezone=True), nullable=True)
    server_received_at = Column(DateTime(timezone=True), server_default=func.now())
    extension_version = Column(String(20), nullable=True)

    # Privacy flags
    anonymized = Column(Boolean, default=False)
    anonymized_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<BrowsingSession {self.session_id} at {self.hour_key}>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "hour_key": self.hour_key,
            "duration_minutes": self.duration_minutes,
            "category_distribution": {
                "work": self.work_time,
                "leisure": self.leisure_time,
                "social": self.social_time,
                "neutral": self.neutral_time
            },
            "metrics": {
                "tab_switches": self.tab_switches,
                "window_focus_changes": self.window_focus_changes,
                "avg_focus_duration_minutes": self.avg_focus_duration_minutes,
                "distraction_rate_per_hour": self.distraction_rate_per_hour,
                "unique_domains": self.unique_domains
            },
            "event_count": self.event_count
        }


class UserExtensionConsent(Base):
    """
    User consent tracking for GDPR/CCPA compliance.
    Tracks consent version, grants, and revocations.
    """
    __tablename__ = "user_extension_consent"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # Optional: link to user account
    extension_install_id = Column(String(100), unique=True, nullable=False, index=True)

    # Consent state
    current_version = Column(String(20), nullable=False)  # e.g., "1.0.0"
    consent_granted = Column(Boolean, default=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Data collection state
    data_collection_active = Column(Boolean, default=False)

    # Consent history (JSON array of version changes)
    consent_history = Column(JSON, default=list)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Privacy preferences
    privacy_mode = Column(String(20), default="balanced")  # strict, balanced, minimal

    def __repr__(self):
        return f"<UserExtensionConsent {self.extension_install_id} v{self.current_version}>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "extension_install_id": self.extension_install_id,
            "current_version": self.current_version,
            "consent_granted": self.consent_granted,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "data_collection_active": self.data_collection_active,
            "privacy_mode": self.privacy_mode
        }


class ConsentVersion(Base):
    """
    Consent version definitions.
    Defines what each version of consent covers.
    """
    __tablename__ = "consent_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(20), unique=True, nullable=False, index=True)
    effective_date = Column(DateTime(timezone=True), nullable=False)
    changelog = Column(Text, nullable=True)
    requires_reconsent = Column(Boolean, default=False)
    data_retention_policy = Column(String(50), default="keep")  # keep, anonymize, delete

    # Features included in this version
    features = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ConsentVersion {self.version}>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "version": self.version,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "changelog": self.changelog,
            "requires_reconsent": self.requires_reconsent,
            "features": self.features
        }


class ExtensionAnalytics(Base):
    """
    Anonymized analytics about extension usage.
    Used for improving the extension and understanding patterns.
    """
    __tablename__ = "extension_analytics"

    id = Column(Integer, primary_key=True, index=True)

    # Anonymous identifiers (hashed)
    anonymous_id = Column(String(64), nullable=False, index=True)

    # Usage metrics
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=True)
    metric_data = Column(JSON, nullable=True)

    # Context
    extension_version = Column(String(20), nullable=True)
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # Temporal
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<ExtensionAnalytics {self.metric_name}={self.metric_value}>"
