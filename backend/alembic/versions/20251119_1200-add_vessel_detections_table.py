"""add vessel detections table

Revision ID: add_vessel_detections
Revises: 
Create Date: 2025-11-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = 'add_vessel_detections'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add vessel_detections table for maritime monitoring."""
    # Ensure PostGIS extension is enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create vessel_detections table
    op.create_table(
        'vessel_detections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geom', geoalchemy2.Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('scene_id', sa.String(length=255), nullable=False),
        sa.Column('detection_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('intensity_db', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('vessel_length_m', sa.Float(), nullable=True),
        sa.Column('vessel_heading_deg', sa.Float(), nullable=True),
        sa.Column('in_river_mouth', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('in_port_zone', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('near_flood_plume', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('detector_type', sa.String(length=50), nullable=False, server_default='cfar'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_vessel_detections_id', 'vessel_detections', ['id'], unique=False)
    op.create_index('ix_vessel_detections_scene_id', 'vessel_detections', ['scene_id'], unique=False)
    op.create_index('ix_vessel_detections_detection_time', 'vessel_detections', ['detection_time'], unique=False)
    
    # Create spatial index for geom column using PostGIS
    op.execute('CREATE INDEX IF NOT EXISTS idx_vessel_detections_geom ON vessel_detections USING GIST (geom)')


def downgrade() -> None:
    """Remove vessel_detections table."""
    # Drop indexes first
    op.execute('DROP INDEX IF EXISTS idx_vessel_detections_geom')
    op.drop_index('ix_vessel_detections_detection_time', table_name='vessel_detections')
    op.drop_index('ix_vessel_detections_scene_id', table_name='vessel_detections')
    op.drop_index('ix_vessel_detections_id', table_name='vessel_detections')
    
    # Drop table
    op.drop_table('vessel_detections')

