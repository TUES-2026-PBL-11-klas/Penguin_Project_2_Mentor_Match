from datetime import datetime, time, timezone

from flask import Flask

from app.db.models import Availability, Review, Session, Subject, User
from app.db.session import SessionLocal


def register_seed_commands(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command() -> None:
        seed_database()
        print("Seed data inserted.")


def seed_database() -> None:
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter_by(email="mentor.math@mentormatch.dev").first()
        if existing_user:
            return

        math = Subject(name="Mathematics", description="Algebra, geometry and exam preparation.")
        physics = Subject(name="Physics", description="Mechanics and introductory problem solving.")
        english = Subject(name="English", description="Grammar, writing and conversation practice.")
        db.add_all([math, physics, english])
        db.flush()

        mentor_1 = User(
            first_name="Elena",
            last_name="Petrova",
            email="mentor.math@mentormatch.dev",
            password_hash="seeded-password-hash",
            role="mentor",
            bio="Mentor focused on algebra and national exam preparation.",
        )
        mentor_2 = User(
            first_name="Nikola",
            last_name="Georgiev",
            email="mentor.physics@mentormatch.dev",
            password_hash="seeded-password-hash",
            role="mentor",
            bio="Physics mentor with strong fundamentals and practical examples.",
        )
        student_1 = User(
            first_name="Maria",
            last_name="Ivanova",
            email="student.maria@mentormatch.dev",
            password_hash="seeded-password-hash",
            role="student",
            grade_level=11,
        )
        student_2 = User(
            first_name="Ivan",
            last_name="Dimitrov",
            email="student.ivan@mentormatch.dev",
            password_hash="seeded-password-hash",
            role="student",
            grade_level=10,
        )

        mentor_1.subjects.extend([math, english])
        mentor_2.subjects.extend([physics, math])
        db.add_all([mentor_1, mentor_2, student_1, student_2])
        db.flush()

        db.add_all(
            [
                Availability(
                    mentor_id=mentor_1.id,
                    weekday="Monday",
                    start_time=time(16, 0),
                    end_time=time(18, 0),
                ),
                Availability(
                    mentor_id=mentor_1.id,
                    weekday="Wednesday",
                    start_time=time(17, 0),
                    end_time=time(19, 0),
                ),
                Availability(
                    mentor_id=mentor_2.id,
                    weekday="Tuesday",
                    start_time=time(15, 30),
                    end_time=time(18, 30),
                ),
            ]
        )

        completed_session = Session(
            mentor_id=mentor_1.id,
            student_id=student_1.id,
            subject_id=math.id,
            scheduled_at=datetime(2026, 3, 20, 16, 0, tzinfo=timezone.utc),
            status="completed",
            meeting_link="https://meet.example.com/math-session",
            notes="Focused on quadratic equations.",
        )
        upcoming_session = Session(
            mentor_id=mentor_2.id,
            student_id=student_2.id,
            subject_id=physics.id,
            scheduled_at=datetime(2026, 4, 2, 17, 30, tzinfo=timezone.utc),
            status="confirmed",
            meeting_link="https://meet.example.com/physics-session",
            notes="Kinematics exercises.",
        )
        db.add_all([completed_session, upcoming_session])
        db.flush()

        db.add(
            Review(
                session_id=completed_session.id,
                mentor_id=mentor_1.id,
                student_id=student_1.id,
                rating=5,
                comment="Clear explanations and useful homework tips.",
            )
        )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
