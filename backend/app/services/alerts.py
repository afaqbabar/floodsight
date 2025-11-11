"""Alert computation service."""
from datetime import datetime, timezone
from typing import List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Station, Forecast, Alert

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


async def compute_alerts_from_forecasts(db: AsyncSession) -> List[Dict]:
    """
    Compute alerts from recent forecasts.
    
    Logic:
    1. Get all stations
    2. For each station, get recent forecasts (within last 24 hours)
    3. Find maximum discharge in next 72 hours
    4. Determine alert level based on discharge
    5. Calculate probability based on forecast lead time
    
    Returns:
        List of alert dictionaries
    """
    logger.info("Computing alerts from forecasts...")
    
    # Get all stations
    result = await db.execute(select(Station))
    stations = result.scalars().all()
    
    if not stations:
        logger.warning("No stations found for alert computation")
        return []
    
    alerts = []
    now = datetime.now(timezone.utc)
    
    for station in stations:
        # Get recent forecasts for this station (last 6 hours of model runs)
        result = await db.execute(
            select(Forecast)
            .where(Forecast.station_id == station.id)
            .where(Forecast.model_run >= func.now() - func.make_interval(0, 0, 0, 0, 6, 0, 0))
            .order_by(Forecast.discharge_m3s.desc())
            .limit(10)
        )
        forecasts = result.scalars().all()
        
        if not forecasts:
            continue
        
        # Find maximum discharge
        max_forecast = forecasts[0]
        max_discharge = max_forecast.discharge_m3s
        
        # Determine alert level
        alert_level = determine_alert_level(max_discharge)
        
        if alert_level == "normal":
            continue  # No alert needed
        
        # Calculate probability based on lead time
        # Shorter lead time = higher confidence
        lead_hours = max_forecast.lead_hours
        if lead_hours <= 24:
            probability = 0.85
        elif lead_hours <= 48:
            probability = 0.70
        else:
            probability = 0.55
        
        # Generate alert message
        message = (
            f"{alert_level.upper()} flood risk detected. "
            f"Maximum discharge forecast: {max_discharge:.1f} m³/s "
            f"(lead time: {lead_hours}h). "
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
        }
        
        alerts.append(alert_data)
        logger.info(
            f"Alert computed for {station.code}: {alert_level} "
            f"(discharge: {max_discharge:.1f} m³/s)"
        )
    
    logger.info(f"Computed {len(alerts)} alerts from forecasts")
    return alerts


async def create_alerts_from_forecasts(db: AsyncSession) -> int:
    """
    Create alert records in database from forecast data.
    
    Returns:
        Number of alerts created
    """
    logger.info("Creating alerts from forecasts...")
    
    # Compute alerts
    alert_data_list = await compute_alerts_from_forecasts(db)
    
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
    
    # Create new alerts
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
        alerts_created += 1
    
    await db.commit()
    
    logger.info(f"Created {alerts_created} alerts in database")
    return alerts_created

