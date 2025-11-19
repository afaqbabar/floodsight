"""add maritime pricing tiers to users

Revision ID: add_maritime_pricing
Revises: add_flood_plumes
Create Date: 2025-11-19 15:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_maritime_pricing'
down_revision: Union[str, None] = 'add_flood_plumes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add pricing tier column
    op.add_column('users', sa.Column('pricing_tier', sa.String(length=50), server_default='free', nullable=False))
    
    # Add Maritime Edition feature flags
    op.add_column('users', sa.Column('has_maritime_vessel_detection', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('has_maritime_port_monitoring', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('has_maritime_plume_tracking', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'has_maritime_plume_tracking')
    op.drop_column('users', 'has_maritime_port_monitoring')
    op.drop_column('users', 'has_maritime_vessel_detection')
    op.drop_column('users', 'pricing_tier')
