"""Alert computation service."""
from datetime import datetime, timezone
from typing import List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Station, Forecast, Alert

# Import new services
from app.services.alert_rules import alert_rules_engine
from app.services.notifications import notification_service
from app.services.webhooks import webhook_service

logger = get_logger(__name__)

# Discharge thresholds (m³/s) for alert levels
# In production, these would be station-specific and based on historical data
ALERT_THRESHOLDS = {
    "info": 800,      # Low alert
    "warning": 1200,  # Medium alert
    "severe": 1600,   # High alert
    "extreme": 2000,  # Extreme alert
}


def determine_alert_level(discharge: float) -> str:
    """
    Determine alert level based on discharge value.
    
    Args:
        discharge: Discharge in m³/s
        
    Returns:
        Alert level: "info", "warning", "severe", or "extreme"
    """
    if discharge >= ALERT_THRESHOLDS["extreme"]:
        return "extreme"
    elif discharge >= ALERT_THRESHOLDS["severe"]:
        return "severe"
    elif discharge >= ALERT_THRESHOLDS["warning"]:
        return "warning"
    elif discharge >= ALERT_THRESHOLDS["info"]:
        return "info"
    else:
        return "normal"


async def compute_alerts_from_forecasts(db: AsyncSession, send_notifications: bool = True) -> List[Dict]:
    """
    Compute alerts from recent forecasts using custom rules engine.
    
    Logic:
    1. Get all stations
    2. For each station, get recent forecasts (within last 24 hours)
    3. Evaluate custom alert rules (or use defaults)
    4. Create alerts as needed
    5. Send notifications and webhooks
    
    Args:
        db: Database session
        send_notifications: Whether to send notifications (default: True)
    
    Returns:
        List of alert dictionaries
    """
    logger.info("Computing alerts from forecasts with custom rules...")
    
    # Get all stations
    result = await db.execute(select(Station))
    stations = result.scalars().all()
    
    if not stations:
        logger.warning("No stations found for alert computation")
        return []
    
    alerts = []
    now = datetime.now(timezone.utc)
    
    for station in stations:
        # Get recent forecasts for this station (last 24 hours of model runs)
        result = await db.execute(
            select(Forecast)
            .where(Forecast.station_id == station.id)
            .where(Forecast.model_run >= func.now() - func.make_interval(0, 0, 0, 1, 0, 0, 0))
            .order_by(Forecast.discharge_m3s.desc())
            .limit(10)
        )
        forecasts = list(result.scalars().all())
        
        if not forecasts:
            continue
        
        # Evaluate station rules (includes custom and default thresholds)
        rule_result = await alert_rules_engine.evaluate_station_rules(
            station, forecasts, db
        )
        
        if not rule_result:
            continue  # No alert needed
        
        alert_level, probability, reason = rule_result
        
        # Get max discharge for reference
        max_forecast = max(forecasts, key=lambda f: f.discharge_m3s)
        max_discharge = max_forecast.discharge_m3s
        lead_hours = max_forecast.lead_hours
        
        # Generate alert message
        message = (
            f"{alert_level.upper()} flood risk detected. "
            f"Maximum discharge forecast: {max_discharge:.1f} m³/s "
            f"(lead time: {lead_hours}h). "
            f"Reason: {reason}. "
            f"Monitor conditions and prepare appropriate response."
        )
        
        # Create alert dictionary
        alert_data = {
            "station_id": station.id,
            "station_name": station.name,
            "station_code": station.code,
            "level": alert_level,
            "probability": probability,
            "message": message,
            "max_discharge": max_discharge,
            "lead_hours": lead_hours,
            "forecast_time": max_forecast.ts,
            "reason": reason,
        }
        
        alerts.append(alert_data)
        logger.info(
            f"Alert computed for {station.code}: {alert_level} "
            f"(discharge: {max_discharge:.1f} m³/s, reason: {reason})"
        )
    
    logger.info(f"Computed {len(alerts)} alerts from forecasts")
    return alerts


async def create_alerts_from_forecasts(
    db: AsyncSession,
    send_notifications: bool = True,
    send_webhooks: bool = True
) -> int:
    """
    Create alert records in database from forecast data and send notifications.
    
    Args:
        db: Database session
        send_notifications: Whether to send user notifications (default: True)
        send_webhooks: Whether to trigger webhooks (default: True)
    
    Returns:
        Number of alerts created
    """
    logger.info("Creating alerts from forecasts...")
    
    # Compute alerts
    alert_data_list = await compute_alerts_from_forecasts(db, send_notifications=False)
    
    if not alert_data_list:
        logger.info("No alerts to create")
        return 0
    
    # Deactivate existing alerts for these stations
    station_ids = [alert["station_id"] for alert in alert_data_list]
    await db.execute(
        Alert.__table__.update()
        .where(Alert.station_id.in_(station_ids))
        .values(is_active=False)
    )
    
    # Create new alerts and send notifications
    alerts_created = 0
    for alert_data in alert_data_list:
        alert = Alert(
            station_id=alert_data["station_id"],
            level=alert_data["level"],
            probability=alert_data["probability"],
            message=alert_data["message"],
            is_active=True,
        )
        db.add(alert)
        await db.flush()  # Get alert ID
        
        # Get station for notifications
        result = await db.execute(
            select(Station).where(Station.id == alert_data["station_id"])
        )
        station = result.scalar_one()
        
        # Send notifications
        if send_notifications:
            try:
                await notification_service.send_alert_notifications(alert, station, db)
                logger.info(f"Sent notifications for alert {alert.id}")
            except Exception as e:
                logger.error(f"Failed to send notifications for alert {alert.id}: {e}")
        
        # Trigger webhooks
        if send_webhooks:
            try:
                await webhook_service.deliver_alert_to_webhooks(alert, station, db)
                logger.info(f"Triggered webhooks for alert {alert.id}")
            except Exception as e:
                logger.error(f"Failed to trigger webhooks for alert {alert.id}: {e}")
        
        alerts_created += 1
    
    await db.commit()
    
    logger.info(f"Created {alerts_created} alerts in database")
    return alerts_created

