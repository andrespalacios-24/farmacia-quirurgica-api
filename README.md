# Surgical Pharmacy API

> **Asynchronous REST API for managing, delivering, and tracking medical supplies in real time in the operating room.**

---

## Description

System designed to digitize and optimize the traceability of medical supplies during surgical procedures. It allows operating room roles (instrumentalists, assistants, anesthesiologists) to make incremental supply requests, use preconfigured kits, and manage pharmacy dispensing with real-time inventory control.

---

## Features

- **Asynchronous backend**: FastAPI endpoints with `asyncpg` and PostgreSQL.
- **Relational design**: SQLAlchemy 2.0 ORM for complex relationships (Users, Roles, Permissions, Supplies, Batches, Withdrawals, Returns).
- **Secure authentication**: JWT-based stateless authentication with Role-Based Access Control (RBAC).
- **Internationalization (i18n)**: Error messages localized dynamically based on the client's `Accept-Language` header (English and Spanish).
- **Clean architecture**: Clear separation of concerns through Services, Routers, Models, and centralized exception handling.
- **Automated tests**: Integration tests for i18n and validation flows.

---

## Tech Stack

- **Language**: Python 3.12+
- **Web framework**: FastAPI
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (fully async with AsyncSession) + Alembic
- **Data validation**: Pydantic v2 & Pydantic Settings
- **ASGI server**: Uvicorn

---

## Project Structure

```text
farmacia-quirurgica-api/
├── app/
│   ├── main.py          # FastAPI entry point and Swagger UI
│   ├── config.py        # Environment variables reading and validation
│   ├── database.py      # Async engine and session factory
│   ├── api/             # Dependencies and router aggregation
│   ├── core/            # Security, exceptions, i18n
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic DTO validation
│   ├── services/        # Business logic layer
│   └── routers/         # HTTP route controllers
├── tests/               # Automated tests
├── alembic/             # Database migrations
├── .env.example         # Environment variables template
└── requirements.txt     # Project dependencies
Getting Started
Prerequisites
- Python 3.12+
- PostgreSQL 16
Setup
1. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate
2. Install dependencies:
pip install -r requirements.txt
3. Configure environment variables:
cp .env.example .env   # then fill in the values
4. Run database migrations:
alembic upgrade head
5. Seed initial data (roles, permissions, admin user):
python -m app.seed
Run
uvicorn app.main:app --reload
Interactive docs at http://127.0.0.1:8000/docs
Test
python -m pytest

---

## Verificación + commit #6

```bash
git add README.md
git commit -m "docs: standardize README in English"