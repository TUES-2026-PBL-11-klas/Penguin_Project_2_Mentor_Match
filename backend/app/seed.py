from flask import Flask
from app.db.models.subject import Subject
from app.db.session import SessionLocal


def register_seed_commands(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command() -> None:
        seed_subjects()
        print("Seed data inserted.")


def seed_subjects() -> None:
    db = SessionLocal()
    try:
        if db.query(Subject).first():
            print("Subjects already seeded.")
            return

        subjects = [
            # Общообразователни
            Subject(name="Математика",                              category="Общообразователни"),
            Subject(name="Математика-РП",                          category="Общообразователни"),
            Subject(name="Български език и литература",            category="Общообразователни"),
            Subject(name="Английски език",                         category="Общообразователни"),
            Subject(name="Руски",                                  category="Общообразователни"),
            Subject(name="История и цивилизация",                  category="Общообразователни"),
            Subject(name="География",                              category="Общообразователни"),
            Subject(name="Философия",                              category="Общообразователни"),
            Subject(name="Биология",                               category="Общообразователни"),
            Subject(name="Химия",                                  category="Общообразователни"),
            Subject(name="Физика",                                 category="Общообразователни"),
            Subject(name="ВС",                                     category="Общообразователни"),
            Subject(name="ГО",                                     category="Общообразователни"),
            Subject(name="Предприемачество",                       category="Общообразователни"),

            # 8-ми клас
            Subject(name="Увод в програмирането (8-ми клас)",     category="8-ми клас"),

            # 9-ти клас
            Subject(name="Програмиране (9-ти клас)",              category="9-ти клас"),
            Subject(name="Въведение в скриптовите езици",         category="9-ти клас"),
            Subject(name="Градивни елементи (9-ти клас)",         category="9-ти клас"),
            Subject(name="ИТ",                                     category="9-ти клас"),
            Subject(name="Комп. мрежи",                           category="9-ти клас"),
            Subject(name="Електротехника",                         category="9-ти клас"),
            Subject(name="Увод в КМ",                             category="9-ти клас"),

            # 10-ти клас
            Subject(name="Увод в АСД (10-ти клас)",              category="10-ти клас"),
            Subject(name="Увод в ООП (10-ти клас)",              category="10-ти клас"),
            Subject(name="Аналогова схемотехника",                category="10-ти клас"),
            Subject(name="Цифрова схемотехника",                  category="10-ти клас"),
            Subject(name="Увод ВМКС",                             category="10-ти клас"),
            Subject(name="Комп. арх. и периф. устр.",             category="10-ти клас"),
            Subject(name="Увод в КМр",                            category="10-ти клас"),
            

            # 11-ти клас

            Subject(name="ОС",                                     category="11-ти клас"),
            Subject(name="ООП (11-ти клас)",                      category="11-ти клас"),
            Subject(name="Разработка на софтуер",                 category="11-ти клас"),
            Subject(name="ЧЕП (11-ти клас)",                     category="11-ти клас"),
            Subject(name="МОПР",                                   category="11-ти клас"),
            Subject(name="ВМКС (11-ти клас)",                    category="11-ти клас"),
            Subject(name="Бази данни",                            category="11-ти клас"),
            Subject(name="ВОТ",                                    category="11-ти клас"),
            Subject(name="УССС",                                   category="11-ти клас"),
            Subject(name="АПЕ",                                    category="11-ти клас"),
            Subject(name="БОМТ",                                   category="11-ти клас"),
            Subject(name="МПТ",                                    category="11-ти клас"),
            Subject(name="Мрежови техн. и протоколи (11-ти клас)",category="11-ти клас"),
            Subject(name="КТТ",                                    category="11-ти клас"),
            
            # 12-ти клас
            Subject(name="Увод в IoT",                            category="12-ти клас"),
            Subject(name="ЧЕП (12-ти клас)",                     category="12-ти клас"),
            Subject(name="Софтуерно инженерство",                 category="12-ти клас"),
            Subject(name="Мрежови протоколи и технологии (12-ти клас)", category="12-ти клас"),
            Subject(name="Интернет програмиране",                 category="12-ти клас"),
            Subject(name="Програмиране на ВМКС (12-ти клас)",    category="12-ти клас"),
            Subject(name="Приложение с граф. потр. интерфейс",   category="12-ти клас"),
            Subject(name="Компютърна графика и дизайн",          category="12-ти клас"),
            Subject(name="Глобални мрежи",                        category="12-ти клас"),
            Subject(name="ИДКМ",                                   category="12-ти клас"),
            Subject(name="Мрежова и инф. сигурност",             category="12-ти клас"),
            Subject(name="Системна администрация",                category="12-ти клас"),
            Subject(name="ВОТ (12-ти клас)",                     category="12-ти клас"),
        ]

        db.add_all(subjects)
        db.commit()
        print(f"Added {len(subjects)} subjects.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()