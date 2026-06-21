# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Contract Generator** — Sistema web para geração de contratos jurídicos (Prestação de Serviços e Locação de Imóvel) em formatos DOCX e PDF, com autenticação de usuários, consulta de CEP/CNPJ e dashboard de histórico.

## Tech Stack

| Layer       | Technology                            |
|-------------|---------------------------------------|
| Backend     | Python 3 + Flask                      |
| Database    | SQLite + Flask-SQLAlchemy             |
| Auth        | Flask-Login (sessão) + Werkzeug hash  |
| DOCX        | python-docx                           |
| PDF         | fpdf2                                  |
| Frontend    | Jinja2 templates + CSS3               |

> **Nota:** A aplicação ativa é o app Flask em `app/`. As pastas `backend/`
> (protótipo FastAPI), `contract-generator/` (com hífen) e `frontend/`
> (UI estática antiga) são legado e **não** fazem parte do app em execução.

## Project Structure

```
contract-generator/
├── main.py                 # Entrypoint: create_app() + app.run()
├── app/                    # Aplicação Flask (camada web)
│   ├── __init__.py         # App factory: db, login_manager, blueprints
│   ├── auth.py             # Blueprint auth (login/register/logout)
│   ├── contracts.py        # Blueprint contratos (dashboard/new/download/delete)
│   ├── models.py           # Modelos Flask-SQLAlchemy (User, Contract)
│   ├── templates/          # Jinja2: base, login, register, dashboard, new_contract
│   └── static/css/         # Estilos
├── contract_generator/     # Biblioteca de geração de contratos (domínio, sem Flask)
│   ├── models/             # contract.py, party.py, clause.py
│   ├── generators/         # base.py, docx_generator.py, pdf_generator.py
│   ├── services/           # cep_service.py, cnpj_service.py (consultas externas)
│   └── templates/          # locacao.json, servico.json (modelos de cláusulas)
├── tests/                  # Suíte pytest (arquivos ainda vazios)
├── requirements.txt        # Deps de runtime
├── requirements-dev.txt    # Deps de dev (pytest, black, flake8, mypy)
├── pytest.ini
├── .env                    # Secrets (never commit)
└── docker-compose.yml      # Postgres (legado — não usado pelo app SQLite)
```

## Development Commands

```bash
# Ativar o ambiente virtual
source venv/bin/activate

# Rodar a aplicação (http://127.0.0.1:5001)
# Porta padrão 5001 — a 5000 é ocupada pelo AirPlay Receiver no macOS.
# Para outra porta: PORT=8000 python main.py
python main.py

# Instalar dependências de runtime
pip install -r requirements.txt

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar testes
pytest

# Formatação / lint / type-check
black .
flake8 contract_generator/
mypy contract_generator/
```

O banco SQLite (`contracts.db`) é criado automaticamente na primeira execução
via `db.create_all()` no app factory. Não é necessário Docker nem PostgreSQL.

## Environment Variables

O `.env` e o `docker-compose.yml` são legado do protótipo FastAPI/Postgres.
O app Flask atual **não** os consome — a config fica em `app/__init__.py`
(`SECRET_KEY` e `SQLALCHEMY_DATABASE_URI` estão hardcoded).

> ⚠️ `SECRET_KEY` está fixa como `"dev-secret-key-change-in-production"`.
> Trocar por valor vindo do ambiente antes de qualquer deploy.

## Code Conventions

- Rotas organizadas em blueprints Flask: `auth_bp` (`app/auth.py`) e
  `contracts_bp` (`app/contracts.py`), registrados no app factory
- Modelos Flask-SQLAlchemy em `app/models.py`; lógica de domínio (geração,
  serviços, modelos de contrato) isolada em `contract_generator/`
- Geradores estendem `GeradorBase` (`contract_generator/generators/base.py`)
- Senhas com `werkzeug.security` (hash); sessões via Flask-Login
- Sem `print()` em código de produção — usar `logging`

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
