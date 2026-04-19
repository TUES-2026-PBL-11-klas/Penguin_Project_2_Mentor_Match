# MentorMatch

Платформа за peer-to-peer менторство между ученици. По-напредналите ученици предлагат помощ по различни предмети, а търсещите помощ могат да резервират сесии, да оставят отзиви и да получават известия.

---

## Технологии

| Компонент        | Технология                         |
|---               |---                                 |
| Backend          | Python 3.11 + Flask                |
| ORM              | SQLAlchemy 2.0 + Alembic           |
| База данни       | PostgreSQL 16                      |
| Автентикация     | JWT (PyJWT + bcrypt)               |
| Известия         | APScheduler + Web Push (pywebpush) |
| Метрики          | Prometheus Flask Exporter          |
| Контейнеризация  | Docker + Docker Compose            |
| CI/CD            | GitHub Actions                     |
| IaC              | Ansible                            |
| Тестове          | pytest + pytest-cov                |

---

## Архитектура

Проектът следва **Layered Architecture**:

```
Routes → Services → Repositories → Models
```

- **Routes** — Flask Blueprints, HTTP endpoints
- **Services** — бизнес логика, design patterns
- **Repositories** — достъп до базата данни
- **Models** — SQLAlchemy ORM модели

**Design Patterns:**
- **Strategy Pattern** — matching алгоритъм за намиране на ментори
- **Observer Pattern** — известия при промяна на статус на сесия

---

## Структура на проекта

```
backend/
├── app/
│   ├── auth/          # Регистрация, login, JWT, профили
│   ├── sessions/      # Резервации, matching, availability
│   ├── reviews/       # Отзиви и оценки
│   ├── notifications/ # Web Push известия
│   ├── db/            # SQLAlchemy модели и сесия
│   └── common/        # Споделени exceptions и utilities
├── migrations/        # Alembic миграции
├── tests/             # Unit и интеграционни тестове
├── ansible/           # Infrastructure as Code
└── requirements.txt
```

---

## Стартиране

### Изисквания

- Docker Desktop
- Git

### Стъпки

**1. Клонирай репото:**
```bash
git clone https://github.com/TUES-2026-PBL-11-klas/Penguin_Project_2_Mentor_Match.git
cd Penguin_Project_2_Mentor_Match
```

**2. Създай `.env` файл в корена:**
```
POSTGRES_DB=  
POSTGRES_USER= 
POSTGRES_PASSWORD= 
POSTGRES_HOST=
POSTGRES_PORT=
JWT_SECRET=
```

**3. Стартирай с Docker:**
```bash
docker compose up --build
```

**4. В отделен терминал пусни миграциите:**
```bash
docker compose exec backend alembic upgrade head
```

**5. Добави начални данни (предмети):**
```bash
docker compose exec backend flask seed
```

**6. Провери че работи:**
```
http://localhost:5000/api/health
```

---

## API Endpoints

### Auth
| Метод | Endpoint | Описание |
|---|---|---|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET | `/api/auth/profile` | Профил на потребителя |
| PATCH | `/api/auth/profile` | Редактиране на профил |
| POST | `/api/auth/add-role` | Добавяне на роля |
| GET | `/api/auth/mentors` | Списък с ментори |
| GET | `/api/auth/mentors/<id>` | Профил на ментор |
| GET | `/api/auth/subjects` | Всички предмети |

### Sessions
| Метод | Endpoint | Описание |
|---|---|---|
| POST | `/api/sessions/request` | Резервация на сесия |
| GET | `/api/sessions/requests` | Pending заявки (ментор) |
| POST | `/api/sessions/<id>/confirm` | Потвърждаване |
| POST | `/api/sessions/<id>/decline` | Отказване |
| POST | `/api/sessions/<id>/cancel` | Отмяна |
| GET | `/api/sessions/mentor/calendar` | Календар на ментор |
| GET | `/api/sessions/student/calendar` | Календар на ученик |
| GET | `/api/sessions/student/history` | История на ученик |
| POST | `/api/sessions/unavailable` | Маркиране като недостъпен |
| GET | `/api/sessions/mentors/search` | Търсене на ментори |

### Reviews
| Метод | Endpoint | Описание |
|---|---|---|
| POST | `/api/reviews/session/<id>` | Оставяне на отзив |
| GET | `/api/reviews/mentor/<id>` | Отзиви за ментор |

### Notifications
| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/notifications/` | Известия на потребителя |
| POST | `/api/notifications/subscribe` | Web Push абонамент |

### Observability
| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/metrics` | Prometheus метрики |

---

## Setup за разработка

```bash
pip install -r backend/requirements.txt
python -m pre_commit install
```

---

## Тестване

```bash
cd backend
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Deploy с Ansible

```bash
cd backend/ansible
ansible-playbook -i inventory.ini playbook.yml
```

---

## Екип

| Член   | Отговорност                             |
|---     |---                                      |
| Stefan | Auth, JWT, потребителски профили        |
| Maya   | Sessions, matching алгоритъм, booking   |
| Daniel | Reviews, notifications, APScheduler     |
| Milena | DB модели, Alembic миграции, seed данни |
| Lina   | Frontend, Docker, GitHub Actions CI/CD  |