"""align models with er diagram

Revision ID: 20260417_0002
Revises: 20260330_0001
Create Date: 2026-04-17
"""

from alembic import op
import sqlalchemy as sa


revision = "20260417_0002"
down_revision = "20260330_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mentor_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("average_rating", sa.Float(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_sessions", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_mentor_profiles_user_id"),
    )

    op.add_column("users", sa.Column("profile_picture", sa.String(length=255), nullable=True))

    op.add_column("subjects", sa.Column("category", sa.String(length=100), nullable=True))

    op.add_column("mentor_subjects", sa.Column("grade_level", sa.Integer(), nullable=True))

    op.add_column("availabilities", sa.Column("mentor_profile_id", sa.Integer(), nullable=True))
    op.add_column("availabilities", sa.Column("day_of_week", sa.Integer(), nullable=True))
    op.add_column(
        "availabilities",
        sa.Column("is_recurring", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.create_foreign_key(
        "fk_availabilities_mentor_profile_id_mentor_profiles",
        "availabilities",
        "mentor_profiles",
        ["mentor_profile_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("sessions", sa.Column("mentor_profile_id", sa.Integer(), nullable=True))
    op.add_column("sessions", sa.Column("mentee_id", sa.Integer(), nullable=True))
    op.add_column("sessions", sa.Column("duration_minutes", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_sessions_mentor_profile_id_mentor_profiles",
        "sessions",
        "mentor_profiles",
        ["mentor_profile_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_sessions_mentee_id_users",
        "sessions",
        "users",
        ["mentee_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("reviews", sa.Column("reviewer_id", sa.Integer(), nullable=True))
    op.add_column("reviews", sa.Column("reviewed_user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_reviews_reviewer_id_users",
        "reviews",
        "users",
        ["reviewer_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_reviews_reviewed_user_id_users",
        "reviews",
        "users",
        ["reviewed_user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.execute(
        """
        INSERT INTO mentor_profiles (user_id, average_rating, total_sessions)
        SELECT
            u.id,
            COALESCE(
                (
                    SELECT AVG(r.rating)::float
                    FROM reviews r
                    WHERE r.mentor_id = u.id
                ),
                0
            ),
            COALESCE(
                (
                    SELECT COUNT(*)
                    FROM sessions s
                    WHERE s.mentor_id = u.id
                    AND s.status = 'completed'
                ),
                0
            )
        FROM users u
        WHERE u.role = 'mentor'
        """
    )

    op.execute(
        """
        UPDATE availabilities a
        SET mentor_profile_id = mp.id
        FROM mentor_profiles mp
        WHERE mp.user_id = a.mentor_id
        """
    )

    op.execute(
        """
        UPDATE sessions s
        SET mentor_profile_id = mp.id
        FROM mentor_profiles mp
        WHERE mp.user_id = s.mentor_id
        """
    )

    op.execute("UPDATE sessions SET mentee_id = student_id WHERE mentee_id IS NULL")
    op.execute("UPDATE reviews SET reviewer_id = student_id WHERE reviewer_id IS NULL")
    op.execute("UPDATE reviews SET reviewed_user_id = mentor_id WHERE reviewed_user_id IS NULL")

    op.alter_column("mentor_profiles", "average_rating", server_default=None)
    op.alter_column("mentor_profiles", "total_sessions", server_default=None)


def downgrade() -> None:
    op.drop_table("notifications")

    op.drop_constraint("fk_reviews_reviewed_user_id_users", "reviews", type_="foreignkey")
    op.drop_constraint("fk_reviews_reviewer_id_users", "reviews", type_="foreignkey")
    op.drop_column("reviews", "reviewed_user_id")
    op.drop_column("reviews", "reviewer_id")

    op.drop_constraint("fk_sessions_mentee_id_users", "sessions", type_="foreignkey")
    op.drop_constraint("fk_sessions_mentor_profile_id_mentor_profiles", "sessions", type_="foreignkey")
    op.drop_column("sessions", "duration_minutes")
    op.drop_column("sessions", "mentee_id")
    op.drop_column("sessions", "mentor_profile_id")

    op.drop_constraint(
        "fk_availabilities_mentor_profile_id_mentor_profiles", "availabilities", type_="foreignkey"
    )
    op.drop_column("availabilities", "is_recurring")
    op.drop_column("availabilities", "day_of_week")
    op.drop_column("availabilities", "mentor_profile_id")

    op.drop_column("mentor_subjects", "grade_level")
    op.drop_column("subjects", "category")
    op.drop_column("users", "profile_picture")

    op.drop_table("mentor_profiles")
