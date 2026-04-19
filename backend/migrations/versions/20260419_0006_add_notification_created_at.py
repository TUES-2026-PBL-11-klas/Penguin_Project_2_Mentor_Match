"""add created_at to notifications

Revision ID: 20260419_0006
Revises: 20260419_0005
Create Date: 2026-04-19
"""

from alembic import op
import sqlalchemy as sa

revision = "20260419_0006"
down_revision = "20260419_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()"))
    )


def downgrade() -> None:
    op.drop_column("notifications", "created_at")