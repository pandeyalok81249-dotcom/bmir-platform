# AI Resume Intelligence Platform

A production-grade, AI-powered Resume Intelligence Platform built with Flutter (Frontend) and FastAPI (Backend), supporting multi-provider AI (OpenAI & Gemini), deterministic resume parsing, evidence-based ATS and career scoring, live resume building, job matching, and interview coaching.

## Architecture Overview

- **Frontend:** Flutter (Dart) with Material 3 Design System, Riverpod, GoRouter, Dio.
- **Backend:** Python FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 16, Redis 7, Celery/Worker.
- **AI Engine:** Multi-provider abstraction layer supporting OpenAI GPT-4o / GPT-4o-mini and Google Gemini 1.5 Pro / Flash with structured output validation, token tracking, prompt injection mitigation, and evidence grounding.
- **Security:** Argon2id password hashing, JWT with refresh token rotation, strict multi-tenant isolation, MIME validation.

## Directory Structure

```
resume-intelligence-platform/
├── backend/          # FastAPI REST API, SQLAlchemy models, Alembic migrations, AI engine
├── frontend/         # Flutter cross-platform client (mobile, tablet, desktop, web)
├── docker/           # Docker Compose, PostgreSQL & Redis configurations
└── tests/            # End-to-end integration and security test suites
```

## Quick Start (Backend)

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Quick Start (Frontend)

```bash
cd frontend
flutter pub get
flutter run
```

