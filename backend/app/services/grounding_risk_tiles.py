"""Grounding risk tile service for vector tile generation."""
import math
from typing import List, Tuple, Optional
from datetime import datetime, timezone

from sqlalchemy import select, and_, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from shapely.geometry import Point, box
import json

from app.db.models import PortFairway, PortSafeDraughtLog
from app.core.logging import get_logger

logger = get_logger(__name__)

# Standard vessel draught categories (metres)
VESSEL_DRAUGHTS = {
    "small": 2.0,      # Small coastal vessels
    "medium": 5.0,     # General cargo ships
    "large": 10.0,     # Large container ships
    "vlcc": 15.0,      # Very Large Crude Carriers
}


def tile_to_bbox(z: int, x: int, y: int) -> Tuple[float, float, float, float]:
    """
    Convert tile coordinates to bounding box (lon_min, lat_min, lon_max, lat_max).
    
    Uses Web Mercator tile coordinate system (EPSG:3857).
    
    Args:
        z: Zoom level
        x: Tile X coordinate
        y: Tile Y coordinate
    
    Returns:
        Tuple of (lon_min, lat_min, lon_max, lat_max)
    """
    n = 2 ** z
    lon_min = x / n * 360.0 - 180.0
    lat_min_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_min = math.degrees(lat_min_rad)
    
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_max_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    lat_max = math.degrees(lat_max_rad)
    
    return (lon_min, lat_min, lon_max, lat_max)


def calculate_grounding_risk(
    safe_draught_m: float,
    vessel_draught_m: float,
    reference_draught_m: float
) -> Tuple[str, str]:
    """
    Calculate grounding risk level and color.
    
    Risk calculation:
    - clearance = safe_draught - vessel_draught
    - green: clearance > 2m (safe)
    - yellow: 0.5m < clearance <= 2m (caution)
    - red: clearance <= 0.5m (danger)
    
    Args:
        safe_draught_m: Current safe draught in metres
        vessel_draught_m: Vessel draught in metres
        reference_draught_m: Reference draught for the port
    
    Returns:
        Tuple of (risk_level, color_hex)
    """
    clearance = safe_draught_m - vessel_draught_m
    
    if clearance > 2.0:
        return ("safe", "#22c55e")  # green-500
    elif clearance > 0.5:
        return ("caution", "#eab308")  # yellow-500
    else:
        return ("danger", "#ef4444")  # red-500


async def get_grounding_risk_features(
    db: AsyncSession,
    z: int,
    x: int,
    y: int,
    vessel_draught: float = VESSEL_DRAUGHTS["medium"]
) -> List[dict]:
    """
    Get grounding risk features for a tile as GeoJSON.
    
    Args:
        db: Database session
        z: Tile zoom level
        x: Tile X coordinate
        y: Tile Y coordinate
        vessel_draught: Vessel draught in metres (default: medium vessel)
    
    Returns:
        List of GeoJSON features with grounding risk
    """
    # Get tile bounding box
    lon_min, lat_min, lon_max, lat_max = tile_to_bbox(z, x, y)
    
    logger.debug(
        f"Fetching grounding risk for tile {z}/{x}/{y}: "
        f"bbox=({lon_min:.2f}, {lat_min:.2f}, {lon_max:.2f}, {lat_max:.2f})"
    )
    
    # Query active port fairways within tile bounds
    # Use PostGIS ST_Intersects with bounding box
    bbox_wkt = f"POLYGON(({lon_min} {lat_min}, {lon_max} {lat_min}, {lon_max} {lat_max}, {lon_min} {lat_max}, {lon_min} {lat_min}))"
    
    fairways_query = select(PortFairway).where(
        and_(
            PortFairway.is_active == True,
            sql_func.ST_Intersects(
                PortFairway.geom,
                sql_func.ST_GeomFromText(bbox_wkt, 4326)
            )
        )
    )
    
    result = await db.execute(fairways_query)
    fairways = result.scalars().all()
    
    if not fairways:
        logger.debug(f"No port fairways found in tile {z}/{x}/{y}")
        return []
    
    features = []
    
    for fairway in fairways:
        # Get latest safe draught calculation
        latest_log_query = select(PortSafeDraughtLog).where(
            PortSafeDraughtLog.port_fairway_id == fairway.id
        ).order_by(PortSafeDraughtLog.calculation_time.desc()).limit(1)
        
        log_result = await db.execute(latest_log_query)
        latest_log = log_result.scalar_one_or_none()
        
        if not latest_log:
            logger.debug(f"No safe draught log for port {fairway.name}, skipping")
            continue
        
        # Calculate grounding risk
        risk_level, color = calculate_grounding_risk(
            latest_log.safe_draught_m,
            vessel_draught,
            fairway.reference_draught_m
        )
        
        clearance = latest_log.safe_draught_m - vessel_draught
        
        # Convert geometry to GeoJSON
        from geoalchemy2.shape import to_shape
        geom_shape = to_shape(fairway.geom)
        geojson_geom = {
            "type": "Polygon",
            "coordinates": [list(geom_shape.exterior.coords)]
        }
        
        feature = {
            "type": "Feature",
            "geometry": geojson_geom,
            "properties": {
                "port_name": fairway.name,
                "port_code": fairway.port_code,
                "safe_draught_m": round(latest_log.safe_draught_m, 2),
                "vessel_draught_m": vessel_draught,
                "clearance_m": round(clearance, 2),
                "risk_level": risk_level,
                "color": color,
                "reference_draught_m": fairway.reference_draught_m,
                "river_name": fairway.river_name,
                "calculation_time": latest_log.calculation_time.isoformat(),
            }
        }
        
        features.append(feature)
        
        logger.debug(
            f"Port {fairway.name}: safe={latest_log.safe_draught_m:.2f}m, "
            f"vessel={vessel_draught:.2f}m, clearance={clearance:.2f}m, risk={risk_level}"
        )
    
    logger.info(f"Returning {len(features)} grounding risk features for tile {z}/{x}/{y}")
    
    return features


async def generate_mvt_tile(
    db: AsyncSession,
    z: int,
    x: int,
    y: int,
    vessel_draught: float = VESSEL_DRAUGHTS["medium"]
) -> Optional[bytes]:
    """
    Generate Mapbox Vector Tile (MVT) for grounding risk.
    
    For simplicity, this returns GeoJSON that can be converted to MVT
    by the client or a proxy service like Mapbox GL JS.
    
    For production, you'd use a library like `mapbox_vector_tile` to
    generate actual .pbf tiles.
    
    Args:
        db: Database session
        z: Tile zoom level
        x: Tile X coordinate  
        y: Tile Y coordinate
        vessel_draught: Vessel draught in metres
    
    Returns:
        MVT tile as bytes (or None if empty)
    """
    features = await get_grounding_risk_features(db, z, x, y, vessel_draught)
    
    if not features:
        return None
    
    # For now, return GeoJSON wrapped as a tile
    # In production, convert to actual MVT format
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return json.dumps(geojson).encode('utf-8')

