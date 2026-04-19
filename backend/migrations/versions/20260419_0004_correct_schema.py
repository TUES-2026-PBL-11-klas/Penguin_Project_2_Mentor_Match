"""correct schema with UUID ids

Revision ID: 20260419_0004
Revises: 20260419_0003
Create Date: 2026-04-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260419_0004"
down_revision = "20260419_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS push_subscriptions CASCADE")
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
    op.execute("DROP TABLE IF EXISTS reviews CASCADE")
    op.execute("DROP TABLE IF EXISTS sessions CASCADE")
    op.execute("DROP TABLE IF EXISTS unavailable_slots CASCADE")
    op.execute("DROP TABLE IF EXISTS availabilities CASCADE")
    op.execute("DROP TABLE IF EXISTS mentor_subjects CASCADE")
    op.execute("DROP TABLE IF EXISTS mentor_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS subjects CASCADE")
    op.execute("DROP TYPE IF EXISTS user_role CASCADE")
    op.execute("DROP TYPE IF EXISTS session_status CASCADE")
    op.execute("DROP TYPE IF EXISTS user_role_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS session_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS notification_type_enum CASCADE")

    op.execute("CREATE TYPE user_role_enum AS ENUM ('student', 'mentor', 'both')")
    op.execute("CREATE TYPE session_status_enum AS ENUM ('pending', 'confirmed', 'completed', 'declined', 'cancelled')")
    op.execute("CREATE TYPE notification_type_enum AS ENUM ('new_request', 'session_confirmed', 'session_declined', 'session_reminder', 'rate_session')")

    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            grade INTEGER NOT NULL,
            class_letter VARCHAR(1) NOT NULL,
            role user_role_enum NOT NULL DEFAULT 'student',
            profile_picture VARCHAR(500),
            bio TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE subjects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            category VARCHAR(100)
        )
    """)

    op.execute("""
        CREATE TABLE mentor_subjects (
            id UUID PRIMARY KEY,
            mentor_id UUID NOT NULL REFERENCES users(id),
            subject_id INTEGER NOT NULL REFERENCES subjects(id),
            grade_level INTEGER
        )
    """)

    op.execute("""
        CREATE TABLE availabilities (
            id UUID PRIMARY KEY,
            mentor_id UUID NOT NULL REFERENCES users(id),
            day_of_week INTEGER NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            is_recurring BOOLEAN NOT NULL DEFAULT true
        )
    """)

    op.execute("""
        CREATE TABLE unavailable_slots (
            id UUID PRIMARY KEY,
            mentor_id UUID NOT NULL REFERENCES users(id),
            start_datetime TIMESTAMP NOT NULL,
            end_datetime TIMESTAMP NOT NULL,
            reason VARCHAR(255)
        )
    """)

    op.execute("""
        CREATE TABLE sessions (
            id UUID PRIMARY KEY,
            mentor_id UUID NOT NULL REFERENCES users(id),
            mentee_id UUID NOT NULL REFERENCES users(id),
            subject_id INTEGER NOT NULL REFERENCES subjects(id),
            scheduled_at TIMESTAMP NOT NULL,
            end_at TIMESTAMP NOT NULL,
            duration_minutes INTEGER NOT NULL,
            status session_status_enum NOT NULL DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE reviews (
            id UUID PRIMARY KEY,
            session_id UUID NOT NULL UNIQUE REFERENCES sessions(id),
            reviewer_id UUID NOT NULL REFERENCES users(id),
            reviewed_user_id UUID NOT NULL REFERENCES users(id),
            rating INTEGER NOT NULL CHECK (rating >= 0 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE notifications (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id),
            session_id UUID REFERENCES sessions(id),
            type notification_type_enum NOT NULL,
            message VARCHAR(500) NOT NULL,
            is_read BOOLEAN NOT NULL DEFAULT false,
            scheduled_at TIMESTAMP,
            sent_at TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE push_subscriptions (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id),
            endpoint TEXT NOT NULL,
            auth VARCHAR(255) NOT NULL,
            p256dh VARCHAR(255) NOT NULL
        )
    """)


def downgrade() -> None:
    op.drop_table("push_subscriptions")
    op.drop_table("notifications")
    op.drop_table("reviews")
    op.drop_table("sessions")
    op.drop_table("unavailable_slots")
    op.drop_table("availabilities")
    op.drop_table("mentor_subjects")
    op.drop_table("subjects")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS notification_type_enum")
    op.execute("DROP TYPE IF EXISTS session_status_enum")
    op.execute("DROP TYPE IF EXISTS user_role_enum")