"""remove bio from users

Revision ID: 20260419_0005
Revises: 20260419_0004
Create Date: 2026-04-19
"""

from alembic import op

revision = "20260419_0005"
down_revision = "20260419_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("users", "bio")


def downgrade() -> None:
    import sqlalchemy as sa
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))