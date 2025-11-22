"""Analytics endpoints for alerts and notifications."""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    AlertAnalytics,
    NotificationAnalytics,
)
from app.core.logging import get_logger
from app.db.models import (
    Alert,
    AlertAcknowledgment,
    NotificationLog,
    Station,
)
from app.db.session import get_db

logger = get_logger(__name__)

router = APIRouter()


@router.get("/analytics/alerts", response_model=AlertAnalytics, tags=["Analytics"])
async def get_alert_analytics(
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
) -> AlertAnalytics:
    """
    Get alert analytics for the specified time period.
    
    Returns statistics on:
    - Total alerts
    - Active alerts
    - Alerts by level
    - Alerts by station
    - Acknowledgment rate
    - Average response time
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Total alerts
    result = await db.execute(
        select(func.count(Alert.id))
        .where(Alert.created_at >= cutoff_date)
    )
    total_alerts = result.scalar() or 0
    
    # Active alerts
    result = await db.execute(
        select(func.count(Alert.id))
        .where(Alert.is_active == True)  # noqa: E712
    )
    active_alerts = result.scalar() or 0
    
    # Alerts by level
    result = await db.execute(
        select(Alert.level, func.count(Alert.id))
        .where(Alert.created_at >= cutoff_date)
        .group_by(Alert.level)
    )
    by_level = {row[0]: row[1] for row in result}
    
    # Fill in missing levels
    for level in ["info", "warning", "severe", "extreme"]:
        if level not in by_level:
            by_level[level] = 0
    
    # Alerts by station (top 10)
    result = await db.execute(
        select(
            Station.code,
            Station.name,
            func.count(Alert.id).label("alert_count")
        )
        .join(Alert, Alert.station_id == Station.id)
        .where(Alert.created_at >= cutoff_date)
        .group_by(Station.id, Station.code, Station.name)
        .order_by(func.count(Alert.id).desc())
        .limit(10)
    )
    by_station = [
        {
            "station_code": row[0],
            "station_name": row[1],
            "alert_count": row[2]
        }
        for row in result
    ]
    
    # Acknowledgment rate
    result = await db.execute(
        select(func.count(Alert.id))
        .where(Alert.created_at >= cutoff_date)
    )
    total_for_ack_rate = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(func.distinct(AlertAcknowledgment.alert_id)))
        .join(Alert, Alert.id == AlertAcknowledgment.alert_id)
        .where(Alert.created_at >= cutoff_date)
    )
    acknowledged_count = result.scalar() or 0
    
    acknowledgment_rate = (
        (acknowledged_count / total_for_ack_rate * 100)
        if total_for_ack_rate > 0
        else 0.0
    )
    
    # Average response time (time from alert issued to first acknowledgment)
    result = await db.execute(
        select(
            func.avg(
                func.extract('epoch', AlertAcknowledgment.acknowledged_at - Alert.issued_at) / 60
            )
        )
        .join(Alert, Alert.id == AlertAcknowledgment.alert_id)
        .where(Alert.created_at >= cutoff_date)
    )
    avg_response_time_minutes = result.scalar()
    
    return AlertAnalytics(
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        by_level=by_level,
        by_station=by_station,
        acknowledgment_rate=round(acknowledgment_rate, 2),
        avg_response_time_minutes=round(avg_response_time_minutes, 2) if avg_response_time_minutes else None,
    )


@router.get("/analytics/notifications", response_model=NotificationAnalytics, tags=["Analytics"])
async def get_notification_analytics(
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
) -> NotificationAnalytics:
    """
    Get notification analytics for the specified time period.
    
    Returns statistics on:
    - Total notifications sent
    - Notifications by type
    - Success rate
    - Failed notifications
    - Performance by provider
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Total notifications
    result = await db.execute(
        select(func.count(NotificationLog.id))
        .where(NotificationLog.created_at >= cutoff_date)
    )
    total_sent = result.scalar() or 0
    
    # Notifications by type
    result = await db.execute(
        select(NotificationLog.notification_type, func.count(NotificationLog.id))
        .where(NotificationLog.created_at >= cutoff_date)
        .group_by(NotificationLog.notification_type)
    )
    by_type = {row[0]: row[1] for row in result}
    
    # Success count
    result = await db.execute(
        select(func.count(NotificationLog.id))
        .where(NotificationLog.created_at >= cutoff_date)
        .where(NotificationLog.status == "sent")
    )
    success_count = result.scalar() or 0
    
    # Failed count
    result = await db.execute(
        select(func.count(NotificationLog.id))
        .where(NotificationLog.created_at >= cutoff_date)
        .where(NotificationLog.status == "failed")
    )
    failed_count = result.scalar() or 0
    
    # Success rate
    success_rate = (
        (success_count / total_sent * 100)
        if total_sent > 0
        else 0.0
    )
    
    # By provider
    result = await db.execute(
        select(
            NotificationLog.provider,
            NotificationLog.status,
            func.count(NotificationLog.id)
        )
        .where(NotificationLog.created_at >= cutoff_date)
        .where(NotificationLog.provider.isnot(None))
        .group_by(NotificationLog.provider, NotificationLog.status)
    )
    
    by_provider: Dict[str, Dict[str, int]] = {}
    for provider, status, count in result:
        if provider not in by_provider:
            by_provider[provider] = {"sent": 0, "failed": 0}
        by_provider[provider][status] = count
    
    return NotificationAnalytics(
        total_sent=total_sent,
        by_type=by_type,
        success_rate=round(success_rate, 2),
        failed_count=failed_count,
        by_provider=by_provider,
    )


@router.get("/analytics/alerts/timeline", tags=["Analytics"])
async def get_alert_timeline(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get alert timeline data for charting.
    
    Returns daily counts of alerts by level.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.date(Alert.issued_at).label("date"),
            Alert.level,
            func.count(Alert.id).label("count")
        )
        .where(Alert.issued_at >= cutoff_date)
        .group_by(func.date(Alert.issued_at), Alert.level)
        .order_by(func.date(Alert.issued_at))
    )
    
    timeline_data = [
        {
            "date": str(row[0]),
            "level": row[1],
            "count": row[2]
        }
        for row in result
    ]
    
    return timeline_data


@router.get("/analytics/stations/risk-ranking", tags=["Analytics"])
async def get_station_risk_ranking(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get stations ranked by flood risk (based on alert frequency and severity).
    
    Risk score calculation:
    - info alert = 1 point
    - warning alert = 2 points
    - severe alert = 4 points
    - extreme alert = 8 points
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get alerts with level weights
    result = await db.execute(
        select(
            Station.id,
            Station.code,
            Station.name,
            Station.river_basin,
            func.count(Alert.id).label("total_alerts"),
            func.sum(
                func.case(
                    (Alert.level == "info", 1),
                    (Alert.level == "warning", 2),
                    (Alert.level == "severe", 4),
                    (Alert.level == "extreme", 8),
                    else_=0
                )
            ).label("risk_score")
        )
        .join(Alert, Alert.station_id == Station.id)
        .where(Alert.issued_at >= cutoff_date)
        .group_by(Station.id, Station.code, Station.name, Station.river_basin)
        .order_by(func.sum(
            func.case(
                (Alert.level == "info", 1),
                (Alert.level == "warning", 2),
                (Alert.level == "severe", 4),
                (Alert.level == "extreme", 8),
                else_=0
            )
        ).desc())
        .limit(20)
    )
    
    ranking = [
        {
            "rank": idx + 1,
            "station_id": row[0],
            "station_code": row[1],
            "station_name": row[2],
            "river_basin": row[3],
            "total_alerts": row[4],
            "risk_score": float(row[5]) if row[5] else 0.0
        }
        for idx, row in enumerate(result)
    ]
    
    return ranking



