"""add grade, class_letter and both role to users

Revision ID: 20260419_0003
Revises: 625e44e5ce45
Create Date: 2026-04-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260419_0003"
down_revision = "625e44e5ce45"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add grade column
    op.add_column("users", sa.Column("grade", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("class_letter", sa.String(length=1), nullable=True))

    # Add 'both' to the user_role enum
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'both'")

    # Copy grade_level to grade for existing rows
    op.execute("UPDATE users SET grade = grade_level WHERE grade IS NULL")


def downgrade() -> None:
    op.drop_column("users", "class_letter")
    op.drop_column("users", "grade")