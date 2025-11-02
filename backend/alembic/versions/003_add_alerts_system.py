"""Add alerts system tables

Revision ID: 003
Revises: ca5cddb72444
Create Date: 2025-11-01 19:40:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '003'
down_revision = 'ca5cddb72444'
branch_labels = None
depends_on = None


def upgrade():
    # Users table (simplified - in production use proper auth)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Alerts table
    op.create_table('alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),  # 'threshold', 'regional', 'impact'
        sa.Column('threshold_probability', sa.Float(), nullable=True),
        sa.Column('threshold_horizon', sa.String(10), nullable=True),  # '24h', '48h'
        sa.Column('location_lat', sa.Float(), nullable=True),
        sa.Column('location_lon', sa.Float(), nullable=True),
        sa.Column('location_name', sa.String(255), nullable=True),
        sa.Column('notification_methods', sa.String(255), nullable=False),  # JSON: ['email', 'webhook']
        sa.Column('webhook_url', sa.String(500), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Alert history table
    op.create_table('alert_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(), nullable=False),
        sa.Column('probability_24h', sa.Float(), nullable=False),
        sa.Column('probability_48h', sa.Float(), nullable=True),
        sa.Column('risk_level_24h', sa.String(50), nullable=False),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('notification_error', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('idx_alerts_user_id', 'alerts', ['user_id'])
    op.create_index('idx_alerts_enabled', 'alerts', ['enabled'])
    op.create_index('idx_alert_history_alert_id', 'alert_history', ['alert_id'])
    op.create_index('idx_alert_history_triggered_at', 'alert_history', ['triggered_at'])


def downgrade():
    op.drop_index('idx_alert_history_triggered_at')
    op.drop_index('idx_alert_history_alert_id')
    op.drop_index('idx_alerts_enabled')
    op.drop_index('idx_alerts_user_id')
    op.drop_table('alert_history')
    op.drop_table('alerts')
    op.drop_table('users')
