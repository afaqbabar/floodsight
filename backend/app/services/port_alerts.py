"""Alert generation service for port siltation and safe draught monitoring."""
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Alert, PortFairway, PortSafeDraughtLog
from app.core.logging import get_logger

logger = get_logger(__name__)

# Safe draught alert thresholds (in metres reduction)
DRAUGHT_REDUCTION_WARNING = 0.5  # Alert when draught reduced by >= 0.5m
DRAUGHT_REDUCTION_CRITICAL = 1.0  # Alert when draught reduced by >= 1.0m


async def check_port_safe_draught_alerts(db: AsyncSession) -> List[Alert]:
    """
    Check all ports for safe draught reductions and create alerts.
    
    Creates alerts when safe draught is reduced by >= 0.5m from reference.
    
    Args:
        db: Database session
    
    Returns:
        List of created alerts
    """
    logger.info("Checking port safe draught alerts...")
    
    # Get all active ports
    ports_query = select(PortFairway).where(
        PortFairway.is_active == True
    )
    
    result = await db.execute(ports_query)
    ports = result.scalars().all()
    
    alerts_created = []
    
    for port in ports:
        # Get most recent safe draught calculation
        log_query = select(PortSafeDraughtLog).where(
            PortSafeDraughtLog.port_fairway_id == port.id
        ).order_by(desc(PortSafeDraughtLog.calculation_time)).limit(1)
        
        result = await db.execute(log_query)
        latest_log = result.scalar_one_or_none()
        
        if not latest_log:
            logger.debug(f"No safe draught logs found for port {port.name}")
            continue
        
        # Calculate draught reduction from reference
        draught_reduction = port.reference_draught_m - latest_log.safe_draught_m
        
        # Determine severity
        if draught_reduction >= DRAUGHT_REDUCTION_CRITICAL:
            severity = "EXTREME"
            alert_type = "port_safe_draught_critical"
            title = f"🚨 Critical: Port {port.name} Safe Draught Reduced"
            message = (
                f"Safe draught at {port.name} critically reduced to {latest_log.safe_draught_m:.1f}m "
                f"(reduction: {draught_reduction:.1f}m from {port.reference_draught_m:.1f}m reference). "
                f"Navigation may be restricted. Current siltation: {latest_log.siltation_depth_m:.2f}m."
            )
        elif draught_reduction >= DRAUGHT_REDUCTION_WARNING:
            severity = "SEVERE"
            alert_type = "port_safe_draught_reduced"
            title = f"⚠️ Port {port.name} Safe Draught Reduced"
            message = (
                f"Safe draught at {port.name} reduced to {latest_log.safe_draught_m:.1f}m "
                f"(reduction: {draught_reduction:.1f}m from {port.reference_draught_m:.1f}m reference). "
                f"Current siltation: {latest_log.siltation_depth_m:.2f}m. Monitor for navigation restrictions."
            )
        else:
            # No alert needed
            continue
        
        # Check if similar alert already exists recently (avoid duplicates)
        recent_alert_query = select(Alert).where(
            and_(
                Alert.alert_type == alert_type,
                Alert.message.contains(port.name),
                Alert.created_at >= datetime.now(timezone.utc) - timedelta(hours=6)
            )
        )
        
        result = await db.execute(recent_alert_query)
        existing_alert = result.scalar_one_or_none()
        
        if existing_alert:
            logger.debug(f"Similar alert already exists for {port.name}, skipping")
            continue
        
        # Create alert
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            station_id=None,  # Port alerts are not station-specific
            forecast_id=None,
            metadata={
                "port_name": port.name,
                "port_code": port.port_code,
                "reference_draught_m": port.reference_draught_m,
                "safe_draught_m": latest_log.safe_draught_m,
                "siltation_depth_m": latest_log.siltation_depth_m,
                "draught_reduction_m": draught_reduction,
                "current_discharge_m3s": latest_log.current_discharge_m3s,
                "risk_level": latest_log.risk_level,
            }
        )
        
        db.add(alert)
        alerts_created.append(alert)
        
        logger.info(
            f"Created {severity} alert for {port.name}: "
            f"draught reduced to {latest_log.safe_draught_m:.1f}m"
        )
    
    if alerts_created:
        await db.commit()
        logger.info(f"Created {len(alerts_created)} port safe draught alerts")
    else:
        logger.info("No port safe draught alerts needed")
    
    return alerts_created


async def check_plume_vessel_alerts(db: AsyncSession) -> List[Alert]:
    """
    Check for high vessel activity in flood plumes.
    
    Creates alerts when plumes have >= 5 dark vessels inside.
    
    Args:
        db: Database session
    
    Returns:
        List of created alerts
    """
    from app.db.models import FloodPlume
    from datetime import timedelta
    
    logger.info("Checking plume vessel alerts...")
    
    # Get recent active plumes (last 24 hours)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    
    plumes_query = select(FloodPlume).where(
        and_(
            FloodPlume.is_active == True,
            FloodPlume.detection_time >= cutoff_time,
            FloodPlume.vessel_count >= 5  # Threshold from spec
        )
    )
    
    result = await db.execute(plumes_query)
    plumes = result.scalars().all()
    
    alerts_created = []
    
    for plume in plumes:
        # Determine severity based on vessel count
        if plume.vessel_count >= 10:
            severity = "EXTREME"
            alert_type = "plume_vessel_influx_critical"
            title = f"🚨 Critical: {plume.vessel_count} Dark Vessels in {plume.river_name} Flood Plume"
            message = (
                f"High nutrient plume detected at {plume.river_name} river mouth with "
                f"{plume.vessel_count} dark vessels inside. Peak discharge: {plume.peak_discharge_m3s:.0f} m³/s, "
                f"plume area: {plume.area_km2:.0f}km². Potential illegal dumping or fishing activity."
            )
        else:  # >= 5 vessels
            severity = "SEVERE"
            alert_type = "plume_vessel_influx"
            title = f"⚠️ {plume.vessel_count} Dark Vessels in {plume.river_name} Flood Plume"
            message = (
                f"Nutrient plume detected at {plume.river_name} river mouth with "
                f"{plume.vessel_count} dark vessels inside. Peak discharge: {plume.peak_discharge_m3s:.0f} m³/s, "
                f"plume area: {plume.area_km2:.0f}km². Monitor for suspicious activity."
            )
        
        # Check if similar alert already exists recently (avoid duplicates)
        recent_alert_query = select(Alert).where(
            and_(
                Alert.alert_type == alert_type,
                Alert.message.contains(plume.river_name),
                Alert.created_at >= datetime.now(timezone.utc) - timedelta(hours=12)
            )
        )
        
        result = await db.execute(recent_alert_query)
        existing_alert = result.scalar_one_or_none()
        
        if existing_alert:
            logger.debug(f"Similar plume alert already exists for {plume.river_name}, skipping")
            continue
        
        # Create alert
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            station_id=None,  # Plume alerts are not station-specific
            forecast_id=None,
            metadata={
                "plume_id": plume.id,
                "river_name": plume.river_name,
                "peak_discharge_m3s": plume.peak_discharge_m3s,
                "area_km2": plume.area_km2,
                "vessel_count": plume.vessel_count,
                "detection_method": plume.detection_method,
                "buffer_radius_km": plume.buffer_radius_km,
            }
        )
        
        db.add(alert)
        alerts_created.append(alert)
        
        logger.info(
            f"Created {severity} alert for {plume.river_name}: "
            f"{plume.vessel_count} vessels in plume"
        )
    
    if alerts_created:
        await db.commit()
        logger.info(f"Created {len(alerts_created)} plume vessel alerts")
    else:
        logger.info("No plume vessel alerts needed")
    
    return alerts_created


async def compute_all_maritime_alerts(db: AsyncSession) -> List[Alert]:
    """
    Compute all maritime-related alerts (port safe draught, vessel influx, etc.).
    
    Args:
        db: Database session
    
    Returns:
        List of created alerts
    """
    logger.info("Computing all maritime alerts...")
    
    all_alerts = []
    
    # Port safe draught alerts
    port_alerts = await check_port_safe_draught_alerts(db)
    all_alerts.extend(port_alerts)
    
    # Plume vessel influx alerts (Phase 3)
    plume_alerts = await check_plume_vessel_alerts(db)
    all_alerts.extend(plume_alerts)
    
    logger.info(f"Total maritime alerts created: {len(all_alerts)}")
    
    return all_alerts

