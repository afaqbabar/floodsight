"""Flood plume detection service for nutrient/sediment monitoring."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
import numpy as np
from sqlalchemy import select, and_, desc, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from geoalchemy2.shape import from_shape, to_shape

from app.db.models import FloodPlume, Forecast, Station, VesselDetection
from app.core.logging import get_logger

logger = get_logger(__name__)

# River mouth coordinates (approximate)
RIVER_MOUTHS = {
    "Elbe": {"lat": 53.9, "lon": 8.7, "basin": "Elbe"},
    "Rhine": {"lat": 51.98, "lon": 4.1, "basin": "Rhine"},
    "Danube": {"lat": 45.2, "lon": 29.7, "basin": "Danube"},
    "Po": {"lat": 44.97, "lon": 12.5, "basin": "Po"},
}


def calculate_buffer_radius(discharge_m3s: float, baseline_discharge: float = 1000.0) -> float:
    """
    Calculate plume buffer radius based on discharge.
    
    Formula: 20km base + scale with discharge
    Range: 20-80km as specified
    
    Args:
        discharge_m3s: Peak discharge in m³/s
        baseline_discharge: Baseline discharge for scaling
    
    Returns:
        Buffer radius in km (20-80 range)
    """
    # Linear scaling: 20km at baseline, 80km at 5x baseline
    ratio = discharge_m3s / baseline_discharge
    radius = 20.0 + min(60.0, (ratio - 1.0) * 15.0)
    
    # Clamp to 20-80km range
    radius = max(20.0, min(80.0, radius))
    
    logger.debug(f"Discharge {discharge_m3s:.0f} m³/s → buffer radius {radius:.1f}km")
    
    return radius


def create_plume_polygon(
    river_mouth_lat: float,
    river_mouth_lon: float,
    buffer_km: float,
    direction: str = "downstream"
) -> Polygon:
    """
    Create a plume polygon extending downstream from river mouth.
    
    Args:
        river_mouth_lat: River mouth latitude
        river_mouth_lon: River mouth longitude
        buffer_km: Buffer radius in km
        direction: "downstream" or "circular"
    
    Returns:
        Shapely Polygon representing plume extent
    """
    # Approximate km to degrees at mid-latitudes (rough conversion)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)
    lat_degrees = buffer_km / 111.0
    lon_degrees = buffer_km / (111.0 * np.cos(np.radians(river_mouth_lat)))
    
    if direction == "circular":
        # Simple circular buffer
        polygon = Point(river_mouth_lon, river_mouth_lat).buffer(lon_degrees)
    else:
        # Downstream-biased polygon (extend seaward, less riverward)
        # Create an ellipse extending more seaward
        points = []
        for angle in np.linspace(0, 2 * np.pi, 50):
            # Bias extension seaward (assume eastward for European rivers)
            r_lat = lat_degrees * 0.5  # Less extension north/south
            r_lon = lon_degrees * 1.5  # More extension east (seaward)
            
            lat = river_mouth_lat + r_lat * np.sin(angle)
            lon = river_mouth_lon + r_lon * np.cos(angle)
            points.append((lon, lat))
        
        polygon = Polygon(points)
    
    logger.debug(
        f"Created plume polygon: center ({river_mouth_lat}, {river_mouth_lon}), "
        f"radius {buffer_km}km"
    )
    
    return polygon


async def detect_plume_synthetic(
    db: AsyncSession,
    river_name: str,
    peak_discharge: Optional[float] = None
) -> Optional[FloodPlume]:
    """
    Create a synthetic plume based on discharge data (proxy for Sentinel-2 detection).
    
    In production, this would:
    1. Download Sentinel-2 scene for river mouth
    2. Calculate B4/B3 ratio (turbidity index)
    3. Threshold at > 1.8
    4. Create polygon from high-turbidity pixels
    
    For now, we create a buffer-based proxy using discharge.
    
    Args:
        db: Database session
        river_name: Name of the river (e.g., "Elbe", "Rhine")
        peak_discharge: Peak discharge in m³/s (if None, fetch from forecasts)
    
    Returns:
        FloodPlume instance or None if no plume detected
    """
    river_name_normalized = river_name.capitalize()
    
    if river_name_normalized not in RIVER_MOUTHS:
        logger.warning(f"River {river_name} not in known river mouths")
        return None
    
    mouth_data = RIVER_MOUTHS[river_name_normalized]
    
    # Get peak discharge if not provided
    if peak_discharge is None:
        # Find station for this river basin
        station_query = select(Station).where(
            Station.river_basin == mouth_data["basin"]
        ).limit(1)
        
        result = await db.execute(station_query)
        station = result.scalar_one_or_none()
        
        if not station:
            logger.warning(f"No station found for river basin {mouth_data['basin']}")
            return None
        
        # Get recent forecast
        forecast_query = select(Forecast).where(
            Forecast.station_id == station.id
        ).order_by(desc(Forecast.created_at)).limit(1)
        
        result = await db.execute(forecast_query)
        forecast = result.scalar_one_or_none()
        
        if not forecast:
            logger.warning(f"No forecast found for station {station.code}")
            return None
        
        peak_discharge = forecast.discharge_m3s
        logger.info(f"Using discharge {peak_discharge:.0f} m³/s from station {station.code}")
    
    # Calculate buffer radius based on discharge
    buffer_km = calculate_buffer_radius(peak_discharge)
    
    # Only create plume if discharge is significantly elevated
    # (proxy for turbidity detection threshold)
    if peak_discharge < 1500.0:  # Below threshold for visible plume
        logger.info(f"Discharge {peak_discharge:.0f} m³/s below plume threshold")
        return None
    
    # Create plume polygon
    plume_geom = create_plume_polygon(
        mouth_data["lat"],
        mouth_data["lon"],
        buffer_km,
        direction="downstream"
    )
    
    # Calculate area
    # Rough approximation: degrees² to km² at mid-latitudes
    area_degrees_sq = plume_geom.area
    area_km2 = area_degrees_sq * (111.0 ** 2) * np.cos(np.radians(mouth_data["lat"]))
    
    # Create plume instance
    plume = FloodPlume(
        geom=from_shape(plume_geom, srid=4326),
        river_name=river_name_normalized,
        river_basin=mouth_data["basin"],
        peak_discharge_m3s=peak_discharge,
        current_discharge_m3s=peak_discharge,
        detection_time=datetime.now(timezone.utc),
        source_scene_id=f"SYNTHETIC_{river_name_normalized}_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        turbidity_index=None,  # Would be B4/B3 ratio from Sentinel-2
        area_km2=area_km2,
        buffer_radius_km=buffer_km,
        detection_method="water_mask_expansion",  # Proxy method
        is_active=True,
    )
    
    logger.info(
        f"Detected plume for {river_name}: "
        f"discharge={peak_discharge:.0f} m³/s, "
        f"buffer={buffer_km:.1f}km, "
        f"area={area_km2:.0f}km²"
    )
    
    return plume


async def count_vessels_in_plume(db: AsyncSession, plume: FloodPlume) -> int:
    """
    Count vessels within a plume polygon.
    
    Args:
        db: Database session
        plume: FloodPlume instance
    
    Returns:
        Number of vessels in plume
    """
    # Get plume geometry
    plume_geom = to_shape(plume.geom)
    
    # Query recent vessel detections (last 24 hours)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    
    # Use PostGIS ST_Within to find vessels in plume
    query = select(sql_func.count(VesselDetection.id)).where(
        and_(
            VesselDetection.detection_time >= cutoff_time,
            sql_func.ST_Within(VesselDetection.geom, plume.geom)
        )
    )
    
    result = await db.execute(query)
    vessel_count = result.scalar() or 0
    
    logger.info(f"Found {vessel_count} vessels in plume for {plume.river_name}")
    
    return vessel_count


async def detect_all_river_plumes(db: AsyncSession) -> List[FloodPlume]:
    """
    Detect plumes for all monitored rivers.
    
    Args:
        db: Database session
    
    Returns:
        List of detected FloodPlume instances
    """
    logger.info("Detecting plumes for all rivers...")
    
    plumes = []
    
    for river_name in RIVER_MOUTHS.keys():
        try:
            plume = await detect_plume_synthetic(db, river_name)
            
            if plume:
                # Count vessels in plume
                vessel_count = await count_vessels_in_plume(db, plume)
                plume.vessel_count = vessel_count
                plume.has_vessel_activity = vessel_count > 0
                
                # Save to database
                db.add(plume)
                plumes.append(plume)
                
                logger.info(
                    f"Plume detected: {river_name}, "
                    f"discharge={plume.peak_discharge_m3s:.0f} m³/s, "
                    f"vessels={vessel_count}"
                )
        except Exception as e:
            logger.error(f"Failed to detect plume for {river_name}: {e}", exc_info=True)
    
    if plumes:
        await db.commit()
        logger.info(f"Detected and stored {len(plumes)} plumes")
    else:
        logger.info("No plumes detected")
    
    return plumes


async def get_recent_plumes(
    db: AsyncSession,
    river_name: Optional[str] = None,
    days: int = 7,
    active_only: bool = True
) -> List[FloodPlume]:
    """
    Get recent plumes for a river.
    
    Args:
        db: Database session
        river_name: Filter by river name (None for all)
        days: Number of days to look back
        active_only: Only return active plumes
    
    Returns:
        List of FloodPlume instances
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
    
    query = select(FloodPlume).where(
        FloodPlume.detection_time >= cutoff_time
    )
    
    if river_name:
        query = query.where(FloodPlume.river_name == river_name.capitalize())
    
    if active_only:
        query = query.where(FloodPlume.is_active == True)
    
    query = query.order_by(desc(FloodPlume.detection_time))
    
    result = await db.execute(query)
    plumes = result.scalars().all()
    
    logger.info(
        f"Found {len(plumes)} plumes "
        f"(river={river_name or 'all'}, days={days}, active_only={active_only})"
    )
    
    return list(plumes)

