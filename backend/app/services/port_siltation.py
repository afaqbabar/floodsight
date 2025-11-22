"""Port siltation and safe draught estimation service."""
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
import numpy as np
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape

from app.db.models import PortFairway, PortSafeDraughtLog, Forecast, Station
from app.core.logging import get_logger

logger = get_logger(__name__)

# Siltation model constant (from specification: 0.00012)
SILTATION_COEFFICIENT = 0.00012  # metres of silt per m³/s discharge above baseline


async def calculate_siltation_depth(
    current_discharge_m3s: float,
    baseline_discharge_m3s: float,
) -> float:
    """
    Calculate estimated siltation depth using simple discharge-based model.
    
    Formula (from specification):
        silt_m = max(0, (current_discharge - baseline_discharge) × 0.00012)
    
    Args:
        current_discharge_m3s: Current river discharge in m³/s
        baseline_discharge_m3s: Baseline/normal discharge in m³/s
    
    Returns:
        Estimated siltation depth in metres (always >= 0)
    """
    discharge_delta = current_discharge_m3s - baseline_discharge_m3s
    siltation_m = max(0.0, discharge_delta * SILTATION_COEFFICIENT)
    
    logger.debug(
        f"Siltation calc: discharge_delta={discharge_delta:.1f} m³/s → silt={siltation_m:.3f}m"
    )
    
    return siltation_m


async def get_current_discharge_for_port(
    db: AsyncSession,
    port: PortFairway
) -> Optional[float]:
    """
    Get current discharge for a port from the nearest monitoring station.
    
    Uses the most recent forecast for stations near the port.
    
    Args:
        db: Database session
        port: PortFairway instance
    
    Returns:
        Current discharge in m³/s, or None if no recent data available
    """
    # Get port centroid for spatial query
    port_geom = to_shape(port.geom)
    port_centroid = port_geom.centroid
    
    # Find nearest station on the same river
    query = select(Station).where(
        Station.river_basin == port.river_name
    )
    
    result = await db.execute(query)
    stations = result.scalars().all()
    
    if not stations:
        logger.warning(f"No stations found for port {port.name} on river {port.river_name}")
        return None
    
    # Get the closest station by distance
    # For simplicity, just use the first station on the same river
    station = stations[0]
    
    # Get most recent forecast for this station
    forecast_query = select(Forecast).where(
        Forecast.station_id == station.id
    ).order_by(desc(Forecast.created_at)).limit(1)
    
    result = await db.execute(forecast_query)
    forecast = result.scalar_one_or_none()
    
    if not forecast:
        logger.warning(f"No forecast found for station {station.code}")
        return None
    
    logger.info(
        f"Using discharge from station {station.code}: {forecast.discharge_m3s:.1f} m³/s"
    )
    
    return forecast.discharge_m3s


async def calculate_port_safe_draught(
    db: AsyncSession,
    port_name: str
) -> Optional[dict]:
    """
    Calculate current safe draught for a port.
    
    Args:
        db: Database session
        port_name: Name of the port (e.g., "Port of Duisburg")
    
    Returns:
        Dictionary with safe draught calculation results, or None if port not found
    """
    # Get port fairway
    query = select(PortFairway).where(
        and_(
            PortFairway.name == port_name,
            PortFairway.is_active == True
        )
    )
    
    result = await db.execute(query)
    port = result.scalar_one_or_none()
    
    if not port:
        logger.error(f"Port not found: {port_name}")
        return None
    
    # Get current discharge
    current_discharge = await get_current_discharge_for_port(db, port)
    
    if current_discharge is None:
        logger.error(f"Could not get discharge data for port {port_name}")
        return None
    
    # Calculate siltation depth
    siltation_depth = await calculate_siltation_depth(
        current_discharge,
        port.baseline_discharge_m3s
    )
    
    # Calculate safe draught
    safe_draught = port.reference_draught_m - siltation_depth
    
    # Get previous calculation (24h ago) for trend
    yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
    
    prev_query = select(PortSafeDraughtLog).where(
        and_(
            PortSafeDraughtLog.port_fairway_id == port.id,
            PortSafeDraughtLog.calculation_time >= yesterday
        )
    ).order_by(desc(PortSafeDraughtLog.calculation_time)).limit(1)
    
    result = await db.execute(prev_query)
    prev_log = result.scalar_one_or_none()
    
    draught_change_24h = None
    if prev_log:
        draught_change_24h = safe_draught - prev_log.safe_draught_m
    
    # Determine risk level
    draught_reduction = port.reference_draught_m - safe_draught
    
    if draught_reduction >= 1.0:
        risk_level = "critical"
    elif draught_reduction >= 0.5:
        risk_level = "reduced"
    else:
        risk_level = "normal"
    
    calculation = {
        "port_name": port.name,
        "port_code": port.port_code,
        "calculation_time": datetime.now(timezone.utc),
        "reference_draught_m": port.reference_draught_m,
        "current_discharge_m3s": current_discharge,
        "baseline_discharge_m3s": port.baseline_discharge_m3s,
        "siltation_depth_m": siltation_depth,
        "safe_draught_m": safe_draught,
        "draught_change_24h_m": draught_change_24h,
        "risk_level": risk_level,
    }
    
    logger.info(
        f"Port {port.name}: safe_draught={safe_draught:.2f}m, "
        f"siltation={siltation_depth:.3f}m, risk={risk_level}"
    )
    
    return calculation


async def store_safe_draught_calculation(
    db: AsyncSession,
    calculation: dict
) -> PortSafeDraughtLog:
    """
    Store safe draught calculation in database.
    
    Args:
        db: Database session
        calculation: Calculation result from calculate_port_safe_draught
    
    Returns:
        Created PortSafeDraughtLog instance
    """
    # Get port fairway ID
    query = select(PortFairway).where(
        PortFairway.name == calculation["port_name"]
    )
    
    result = await db.execute(query)
    port = result.scalar_one()
    
    # Create log entry
    log = PortSafeDraughtLog(
        port_fairway_id=port.id,
        calculation_time=calculation["calculation_time"],
        current_discharge_m3s=calculation["current_discharge_m3s"],
        siltation_depth_m=calculation["siltation_depth_m"],
        safe_draught_m=calculation["safe_draught_m"],
        draught_change_24h_m=calculation["draught_change_24h_m"],
        risk_level=calculation["risk_level"],
    )
    
    db.add(log)
    await db.commit()
    await db.refresh(log)
    
    logger.info(f"Stored safe draught log for port {calculation['port_name']}")
    
    return log


async def calculate_all_ports(db: AsyncSession) -> List[dict]:
    """
    Calculate safe draught for all active ports.
    
    Args:
        db: Database session
    
    Returns:
        List of calculation results
    """
    query = select(PortFairway).where(
        PortFairway.is_active == True
    )
    
    result = await db.execute(query)
    ports = result.scalars().all()
    
    calculations = []
    
    for port in ports:
        try:
            calc = await calculate_port_safe_draught(db, port.name)
            if calc:
                calculations.append(calc)
                # Store in database
                await store_safe_draught_calculation(db, calc)
        except Exception as e:
            logger.error(f"Failed to calculate safe draught for port {port.name}: {e}", exc_info=True)
    
    logger.info(f"Calculated safe draught for {len(calculations)} ports")
    
    return calculations

