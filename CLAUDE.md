# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Contract Generator** — Sistema web para geração de contratos jurídicos (Prestação de Serviços e Locação de Imóvel) em formatos DOCX e PDF, com autenticação de usuários, consulta de CEP/CNPJ e dashboard de histórico.

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python 3 + FastAPI                |
| Database    | PostgreSQL + SQLAlchemy           |
| Auth        | JWT (python-jose / passlib)       |
| DOCX/PDF    | python-docx + fpdf2               |
| Frontend    | HTML5 + CSS3 + Vanilla JS         |
| DevOps      | Docker + docker-compose           |

## Project Structure

```
contract-generator/
├── backend/              # FastAPI application
│   ├── main.py           # App entrypoint + routers
│   ├── auth.py           # JWT auth logic
│   ├── models.py         # SQLAlchemy models (User, ContractRecord)
│   ├── schemas.py        # Pydantic schemas
│   └── database.py       # DB engine + session
├── contract-generator/   # Contract generation library
│   ├── api.py            # Internal API helpers
│   └── main.py           # Generation logic
├── frontend/             # Static web UI
│   ├── index.html
│   ├── script.js
│   └── style.css
├── tests/                # pytest test suite
├── docker-compose.yml    # Postgres + app services
├── requirements.txt
└── .env                  # Secrets (never commit)
```

## Development Commands

```bash
# Start database and app
docker-compose up -d

# Run locally (without Docker)
uvicorn backend.main:app --reload

# Run tests
pytest

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Required in `.env` (see `.env.example`):
- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — JWT signing key
- `ALGORITHM` — JWT algorithm (HS256)

## Code Conventions

- FastAPI route handlers in `backend/main.py` grouped by router prefix
- Pydantic schemas in `backend/schemas.py` for all request/response bodies
- SQLAlchemy models in `backend/models.py`
- No `print()` in production code — use Python `logging`
- All API endpoints must return consistent JSON structure

## Git Workflow

- Never push directly to `main`
- Branch naming: `feat/`, `fix/`, `chore/`
- Always run `pytest` before opening a PR

## UI/UX Skill

A skill for UI/UX design intelligence is installed at `.claude/skills/ui-ux-pro-max/`.

Use it for any frontend work. Quick search example:
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard legal SaaS minimal" --design-system
```

Available domains: `product`, `style`, `color`, `typography`, `landing`, `chart`, `ux`
Available stacks: `html-tailwind`, `react`, `nextjs`, `shadcn`, `vue`, `svelte`, and more
