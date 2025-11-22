"""add flood plumes table

Revision ID: 20251119_1400
Revises: 20251119_1330
Create Date: 2025-11-19 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = '20251119_1400'
down_revision: Union[str, None] = '20251119_1330'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create flood_plumes table
    op.create_table(
        "flood_plumes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("geom", Geometry("POLYGON", srid=4326), nullable=False),
        sa.Column("river_name", sa.String(length=255), nullable=False),
        sa.Column("river_basin", sa.String(length=255), nullable=True),
        sa.Column("peak_discharge_m3s", sa.Float(), nullable=False),
        sa.Column("current_discharge_m3s", sa.Float(), nullable=True),
        sa.Column("detection_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_scene_id", sa.String(length=255), nullable=True),
        sa.Column("turbidity_index", sa.Float(), nullable=True),
        sa.Column("area_km2", sa.Float(), nullable=True),
        sa.Column("buffer_radius_km", sa.Float(), nullable=False),
        sa.Column("detection_method", sa.String(length=50), server_default="turbidity", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("has_vessel_activity", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("vessel_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes
    op.create_index(op.f("ix_flood_plumes_id"), "flood_plumes", ["id"], unique=False)
    op.create_index(op.f("ix_flood_plumes_river_name"), "flood_plumes", ["river_name"], unique=False)
    op.create_index(op.f("ix_flood_plumes_detection_time"), "flood_plumes", ["detection_time"], unique=False)
    op.create_index("idx_flood_plumes_geom", "flood_plumes", ["geom"], unique=False, postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("idx_flood_plumes_geom", table_name="flood_plumes", postgresql_using="gist")
    op.drop_index(op.f("ix_flood_plumes_detection_time"), table_name="flood_plumes")
    op.drop_index(op.f("ix_flood_plumes_river_name"), table_name="flood_plumes")
    op.drop_index(op.f("ix_flood_plumes_id"), table_name="flood_plumes")
    op.drop_table("flood_plumes")
