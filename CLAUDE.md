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
| Segurança   | Flask-WTF (CSRF) + Flask-Limiter (rate limit no login) |
| DOCX        | python-docx                           |
| PDF         | fpdf2                                  |
| Frontend    | Jinja2 templates + CSS3 + JS vanilla  |

> **Nota:** A aplicação ativa é o app Flask em `app/`, que usa a biblioteca de
> domínio `contract_generator/` (com underscore). As pastas `backend/`
> (protótipo FastAPI) e `frontend/` (UI estática antiga) são legado e **não**
> fazem parte do app em execução.

## Project Structure

```
contract-generator/
├── main.py                 # Entrypoint: create_app() + app.run()
├── app/                    # Aplicação Flask (camada web)
│   ├── __init__.py         # App factory: db, login_manager, csrf, limiter, blueprints
│   ├── auth.py             # Blueprint auth (login/register/logout + conta self-service)
│   ├── contracts.py        # Blueprint contratos (dashboard/new/download/delete + api/cep)
│   ├── models.py           # Modelos Flask-SQLAlchemy (User, Contract)
│   ├── templates/          # Jinja2: base, login, register, dashboard, new_contract, account*
│   ├── static/css/         # Estilos
│   └── static/js/          # cep.js (autocomplete de endereço)
├── contract_generator/     # Biblioteca de geração de contratos (domínio, sem Flask)
│   ├── models/             # contract.py, party.py, clause.py
│   ├── generators/         # base.py, docx_generator.py, pdf_generator.py
│   ├── services/           # cep_service.py, cnpj_service.py (consultas externas)
│   └── templates/          # locacao.json, servico.json (modelos de cláusulas)
├── tests/                  # Suíte pytest (test_auth.py: isolamento + CRUD)
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

A config fica em `app/__init__.py` e lê do ambiente (via `python-dotenv`, que
carrega o `.env` se existir). Variáveis reconhecidas:

- `SECRET_KEY` — assina as sessões. Se ausente, o app gera uma chave **efêmera**
  com `secrets.token_hex(32)` e loga um warning (as sessões caem a cada
  reinício). Defina em produção. Ver `.env.example`.
- `DATABASE_URL` — URI do SQLAlchemy. Padrão: `sqlite:///contracts.db`.

> O `docker-compose.yml` (Postgres) é legado do protótipo FastAPI e **não** é
> usado pelo app SQLite atual.

## Code Conventions

- Rotas organizadas em blueprints Flask: `auth_bp` (`app/auth.py`) e
  `contracts_bp` (`app/contracts.py`), registrados no app factory
- Modelos Flask-SQLAlchemy em `app/models.py`; lógica de domínio (geração,
  serviços, modelos de contrato) isolada em `contract_generator/`
- Geradores estendem `GeradorBase` (`contract_generator/generators/base.py`)
- Senhas com `werkzeug.security` (hash); sessões via Flask-Login. Força de
  senha validada por `validar_senha()` em `app/auth.py` (≥8, com letra e número)
- Sem `print()` em código de produção — usar `logging`

### Rotas

`auth_bp` (`app/auth.py`):
- `GET/POST /login` — autenticação (rate limit `5/min` no POST via Flask-Limiter)
- `GET/POST /register` — cadastro (login automático após sucesso)
- `GET /logout`
- `GET/POST /account` — editar perfil (nome/e-mail)
- `GET/POST /account/password` — trocar senha (exige a senha atual)
- `POST /account/delete` — excluir a própria conta (cascade nos contratos)

`contracts_bp` (`app/contracts.py`):
- `GET /` — dashboard (lista os contratos do `current_user`)
- `GET/POST /contracts/new` — gerar contrato (DOCX/PDF)
- `GET /contracts/<id>/view` e `/view/pdf` — visualização inline
- `GET /contracts/<id>/download/<fmt>` — download (`docx`/`pdf`)
- `POST /contracts/<id>/delete`
- `GET /api/cep/<cep>` — JSON para autocomplete de endereço (usa `CepService`)

### Segurança

- Todas as rotas de contrato/conta usam `@login_required` e checam
  `record.user_id != current_user.id → abort(403)` (isolamento entre usuários)
- CSRF habilitado globalmente via Flask-WTF: todo `<form method="post">`
  precisa de `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
- `create_app(test_config=None)` aceita overrides para testes (ex.: DB em
  memória, `WTF_CSRF_ENABLED=False`, `RATELIMIT_ENABLED=False`)

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
