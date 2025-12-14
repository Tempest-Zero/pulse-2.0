"""
Extension Router
API endpoints for browser extension integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from models.base import get_db
from models.extension_metadata import (
    BrowsingSession,
    UserExtensionConsent,
    ConsentVersion,
    ExtensionAnalytics
)

router = APIRouter(prefix="/api/v1/extension", tags=["extension"])


# Pydantic schemas for request/response
class SessionMetrics(BaseModel):
    tab_switches: int
    window_focus_changes: int
    avg_focus_duration_minutes: float
    distraction_rate_per_hour: float
    unique_domains: int


class CategoryDistribution(BaseModel):
    work: int
    leisure: int
    social: int
    neutral: int


class BrowsingSessionCreate(BaseModel):
    session_id: str
    timestamp: datetime
    hour_key: str
    duration_minutes: int
    category_distribution: CategoryDistribution
    metrics: SessionMetrics
    event_count: int


class SyncRequest(BaseModel):
    sessions: List[BrowsingSessionCreate]
    timestamp: int


class SyncResponse(BaseModel):
    success: bool
    synced_count: int
    message: str


class ConsentStatusResponse(BaseModel):
    has_consent: bool
    current_version: Optional[str]
    requires_reconsent: bool
    version_info: Optional[dict]


class VersionCheckResponse(BaseModel):
    compatible: bool
    upgrade_required: bool
    message: Optional[str]
    latest_version: str


@router.post("/sync", response_model=SyncResponse)
async def sync_sessions(
    request: SyncRequest,
    x_extension_version: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Sync browsing sessions from extension to backend.

    - Receives aggregated hourly sessions
    - Deduplicates by session_id
    - Stores in database
    """
    try:
        synced_count = 0

        for session_data in request.sessions:
            # Check if session already exists (deduplication)
            existing = db.query(BrowsingSession).filter(
                BrowsingSession.session_id == session_data.session_id
            ).first()

            if existing:
                continue  # Skip duplicates

            # Create new session
            session = BrowsingSession(
                session_id=session_data.session_id,
                timestamp=session_data.timestamp,
                hour_key=session_data.hour_key,
                duration_minutes=session_data.duration_minutes,
                work_time=session_data.category_distribution.work,
                leisure_time=session_data.category_distribution.leisure,
                social_time=session_data.category_distribution.social,
                neutral_time=session_data.category_distribution.neutral,
                tab_switches=session_data.metrics.tab_switches,
                window_focus_changes=session_data.metrics.window_focus_changes,
                avg_focus_duration_minutes=session_data.metrics.avg_focus_duration_minutes,
                distraction_rate_per_hour=session_data.metrics.distraction_rate_per_hour,
                unique_domains=session_data.metrics.unique_domains,
                event_count=session_data.event_count,
                client_timestamp=session_data.timestamp,
                extension_version=x_extension_version
            )

            db.add(session)
            synced_count += 1

        db.commit()

        return SyncResponse(
            success=True,
            synced_count=synced_count,
            message=f"Successfully synced {synced_count} sessions"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/version", response_model=VersionCheckResponse)
async def check_version(
    x_extension_version: Optional[str] = Header(None)
):
    """
    Check extension version compatibility.

    Returns whether the extension version is compatible
    and if an upgrade is required.
    """
    CURRENT_API_VERSION = "1.0.0"
    MINIMUM_EXTENSION_VERSION = "1.0.0"

    compatible = True
    upgrade_required = False
    message = None

    if not x_extension_version:
        return VersionCheckResponse(
            compatible=True,
            upgrade_required=False,
            message="No version header provided",
            latest_version=CURRENT_API_VERSION
        )

    # Simple version comparison (would be more sophisticated in production)
    if x_extension_version < MINIMUM_EXTENSION_VERSION:
        compatible = False
        upgrade_required = True
        message = f"Extension version {x_extension_version} is outdated. Please upgrade to {MINIMUM_EXTENSION_VERSION} or later."

    return VersionCheckResponse(
        compatible=compatible,
        upgrade_required=upgrade_required,
        message=message,
        latest_version=CURRENT_API_VERSION
    )


@router.get("/consent/status", response_model=ConsentStatusResponse)
async def get_consent_status(
    extension_install_id: str,
    db: Session = Depends(get_db)
):
    """
    Get consent status for an extension installation.
    """
    consent = db.query(UserExtensionConsent).filter(
        UserExtensionConsent.extension_install_id == extension_install_id
    ).first()

    if not consent:
        return ConsentStatusResponse(
            has_consent=False,
            current_version=None,
            requires_reconsent=True,
            version_info=None
        )

    # Check if re-consent is needed
    current_version_info = db.query(ConsentVersion).filter(
        ConsentVersion.version == consent.current_version
    ).first()

    # Get latest version
    latest_version = db.query(ConsentVersion).order_by(
        ConsentVersion.effective_date.desc()
    ).first()

    requires_reconsent = False
    if latest_version and latest_version.version != consent.current_version:
        if latest_version.requires_reconsent:
            requires_reconsent = True

    return ConsentStatusResponse(
        has_consent=consent.consent_granted,
        current_version=consent.current_version,
        requires_reconsent=requires_reconsent,
        version_info=latest_version.to_dict() if latest_version else None
    )


@router.post("/consent/grant")
async def grant_consent(
    extension_install_id: str,
    version: str,
    db: Session = Depends(get_db)
):
    """
    Grant consent for data collection.
    """
    # Check if consent record exists
    consent = db.query(UserExtensionConsent).filter(
        UserExtensionConsent.extension_install_id == extension_install_id
    ).first()

    now = datetime.utcnow()

    if consent:
        # Update existing consent
        consent.current_version = version
        consent.consent_granted = True
        consent.granted_at = now
        consent.revoked_at = None
        consent.data_collection_active = True

        # Add to history
        if not consent.consent_history:
            consent.consent_history = []

        consent.consent_history.append({
            "action": "granted",
            "version": version,
            "timestamp": now.isoformat()
        })
    else:
        # Create new consent record
        consent = UserExtensionConsent(
            extension_install_id=extension_install_id,
            current_version=version,
            consent_granted=True,
            granted_at=now,
            data_collection_active=True,
            consent_history=[{
                "action": "granted",
                "version": version,
                "timestamp": now.isoformat()
            }]
        )
        db.add(consent)

    db.commit()

    return {"success": True, "message": "Consent granted"}


@router.post("/consent/revoke")
async def revoke_consent(
    extension_install_id: str,
    db: Session = Depends(get_db)
):
    """
    Revoke consent for data collection.
    """
    consent = db.query(UserExtensionConsent).filter(
        UserExtensionConsent.extension_install_id == extension_install_id
    ).first()

    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")

    now = datetime.utcnow()

    consent.consent_granted = False
    consent.revoked_at = now
    consent.data_collection_active = False

    # Add to history
    if not consent.consent_history:
        consent.consent_history = []

    consent.consent_history.append({
        "action": "revoked",
        "version": consent.current_version,
        "timestamp": now.isoformat()
    })

    db.commit()

    return {"success": True, "message": "Consent revoked"}


@router.get("/sessions/recent")
async def get_recent_sessions(
    limit: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get recent browsing sessions (for testing/debugging).
    Limited to last 24 sessions by default.
    """
    sessions = db.query(BrowsingSession).order_by(
        BrowsingSession.timestamp.desc()
    ).limit(limit).all()

    return [session.to_dict() for session in sessions]


@router.post("/analytics")
async def log_analytics(
    metric_name: str,
    metric_value: Optional[float] = None,
    metric_data: Optional[dict] = None,
    anonymous_id: str = None,
    x_extension_version: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Log anonymized analytics data.
    """
    if not anonymous_id:
        raise HTTPException(status_code=400, detail="anonymous_id is required")

    analytics = ExtensionAnalytics(
        anonymous_id=anonymous_id,
        metric_name=metric_name,
        metric_value=metric_value,
        metric_data=metric_data,
        extension_version=x_extension_version
    )

    db.add(analytics)
    db.commit()

    return {"success": True, "message": "Analytics logged"}
