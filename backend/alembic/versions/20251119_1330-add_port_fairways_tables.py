"""add port fairways and safe draught tables

Revision ID: 20251119_1330
Revises: 20251119_1200
Create Date: 2025-11-19 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251119_1330'
down_revision = '20251119_1200'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add port_fairways and port_safe_draught_logs tables."""
    
    # Create port_fairways table
    op.create_table(
        'port_fairways',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geom', Geometry('POLYGON', srid=4326), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('port_code', sa.String(length=50), nullable=False),
        sa.Column('reference_draught_m', sa.Float(), nullable=False),
        sa.Column('baseline_discharge_m3s', sa.Float(), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('river_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create indexes for port_fairways
    op.create_index('ix_port_fairways_id', 'port_fairways', ['id'], unique=False)
    op.create_index('ix_port_fairways_name', 'port_fairways', ['name'], unique=False)
    op.create_index('ix_port_fairways_port_code', 'port_fairways', ['port_code'], unique=False)
    op.create_index('idx_port_fairways_geom', 'port_fairways', ['geom'], unique=False, postgresql_using='gist')
    
    # Create port_safe_draught_logs table
    op.create_table(
        'port_safe_draught_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('port_fairway_id', sa.Integer(), nullable=False),
        sa.Column('calculation_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_discharge_m3s', sa.Float(), nullable=False),
        sa.Column('siltation_depth_m', sa.Float(), nullable=False),
        sa.Column('safe_draught_m', sa.Float(), nullable=False),
        sa.Column('draught_change_24h_m', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default=sa.text("'normal'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for port_safe_draught_logs
    op.create_index('ix_port_safe_draught_logs_id', 'port_safe_draught_logs', ['id'], unique=False)
    op.create_index('ix_port_safe_draught_logs_port_fairway_id', 'port_safe_draught_logs', ['port_fairway_id'], unique=False)
    op.create_index('ix_port_safe_draught_logs_calculation_time', 'port_safe_draught_logs', ['calculation_time'], unique=False)
    
    # Insert sample port fairways (Duisburg as primary example)
    op.execute("""
        INSERT INTO port_fairways (name, port_code, geom, reference_draught_m, baseline_discharge_m3s, country, river_name)
        VALUES 
        (
            'Port of Duisburg',
            'DEDUISBURG',
            ST_GeomFromText('POLYGON((6.73 51.43, 6.77 51.43, 6.77 51.47, 6.73 51.47, 6.73 51.43))', 4326),
            4.2,
            2200.0,
            'DE',
            'Rhine'
        ),
        (
            'Port of Rotterdam',
            'NLRTM',
            ST_GeomFromText('POLYGON((4.46 51.90, 4.52 51.90, 4.52 51.95, 4.46 51.95, 4.46 51.90))', 4326),
            12.5,
            2400.0,
            'NL',
            'Rhine'
        ),
        (
            'Port of Cologne',
            'DECOLOGNE',
            ST_GeomFromText('POLYGON((6.95 50.93, 6.98 50.93, 6.98 50.95, 6.95 50.95, 6.95 50.93))', 4326),
            3.5,
            2000.0,
            'DE',
            'Rhine'
        );
    """)


def downgrade() -> None:
    """Drop port_fairways and port_safe_draught_logs tables."""
    op.drop_index('ix_port_safe_draught_logs_calculation_time', table_name='port_safe_draught_logs')
    op.drop_index('ix_port_safe_draught_logs_port_fairway_id', table_name='port_safe_draught_logs')
    op.drop_index('ix_port_safe_draught_logs_id', table_name='port_safe_draught_logs')
    op.drop_table('port_safe_draught_logs')
    
    op.drop_index('idx_port_fairways_geom', table_name='port_fairways', postgresql_using='gist')
    op.drop_index('ix_port_fairways_port_code', table_name='port_fairways')
    op.drop_index('ix_port_fairways_name', table_name='port_fairways')
    op.drop_index('ix_port_fairways_id', table_name='port_fairways')
    op.drop_table('port_fairways')

