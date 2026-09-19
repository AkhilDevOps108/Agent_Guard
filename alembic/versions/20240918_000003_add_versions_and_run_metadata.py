"""Add agent versions and evaluation run metadata.

Revision ID: 000000000003
Revises: 000000000002
"""

from alembic import op
import sqlalchemy as sa


revision = "000000000003"
down_revision = "000000000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("agent_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("environment", sa.String(length=64), nullable=False, server_default="development"),
        sa.Column("config", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_id", "version", name="uq_agent_versions_agent_version"),
    )
    op.create_index("ix_agent_versions_agent_id", "agent_versions", ["agent_id"])
    op.add_column("agents", sa.Column("environment", sa.String(length=64), nullable=False, server_default="development"))
    op.add_column("test_runs", sa.Column("agent_version", sa.String(length=64), nullable=False, server_default="1.0.0"))
    op.add_column("test_runs", sa.Column("categories", sa.Text(), nullable=False, server_default="[]"))
    for name in ("critical", "high", "medium", "low"):
        op.add_column("test_runs", sa.Column(name, sa.Integer(), nullable=False, server_default="0"))
    op.add_column("test_runs", sa.Column("deployment_decision", sa.String(length=32), nullable=True))
    op.add_column("test_runs", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.create_index("ix_test_runs_agent_version", "test_runs", ["agent_version"])


def downgrade() -> None:
    op.drop_index("ix_test_runs_agent_version", table_name="test_runs")
    for name in ("completed_at", "deployment_decision", "low", "medium", "high", "critical", "categories", "agent_version"):
        op.drop_column("test_runs", name)
    op.drop_column("agents", "environment")
    op.drop_index("ix_agent_versions_agent_id", table_name="agent_versions")
    op.drop_table("agent_versions")
