"""Add timestamps to registered agents.

Revision ID: 000000000002
Revises: 000000000001
Create Date: 2026-09-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "000000000002"
down_revision = "000000000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.add_column(
        "agents",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_column("agents", "updated_at")
    op.drop_column("agents", "created_at")