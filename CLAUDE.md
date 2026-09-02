# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Contract Generator** — Sistema web para geração de contratos jurídicos (Prestação de Serviços, Locação de Imóvel e Produção Fotográfica) em formatos DOCX e PDF, com autenticação de usuários, consulta de CEP/CNPJ e dashboard de histórico.

## Tech Stack

| Layer       | Technology                            |
|-------------|---------------------------------------|
| Backend     | Python 3 + Flask                      |
| Database    | Flask-SQLAlchemy — SQLite (local) / Neon Postgres (produção) |
| Deploy      | Vercel (serverless, preset `flask`)   |
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
│   ├── clients.py          # Blueprint agenda de clientes (listar/editar/excluir + upsert)
│   ├── contracts.py        # Blueprint contratos (dashboard/new/download/delete + api/cep)
│   ├── models.py           # Modelos Flask-SQLAlchemy (User, ContractRecord, Client)
│   ├── templates/          # Jinja2: base, login, register, dashboard, new_contract, account*, client*
│   ├── static/css/         # Estilos
│   └── static/js/          # cep.js (endereço), clients.js (agenda), contract_fields.js
├── contract_generator/     # Biblioteca de geração de contratos (domínio, sem Flask)
│   ├── models/             # contract.py, party.py, clause.py
│   ├── generators/         # base.py, docx_generator.py, pdf_generator.py
│   ├── services/           # cep_service.py, cnpj_service.py (consultas externas)
│   └── templates/          # locacao.json, servico.json, fotografia.json (cláusulas)
├── tests/                  # Suíte pytest (test_auth.py: isolamento + CRUD)
├── requirements.txt        # Deps de runtime
├── requirements-dev.txt    # Deps de dev (pytest, black, flake8, mypy)
├── pytest.ini
├── vercel.json             # Deploy: preset `flask` (entrypoint = main.py)
├── .vercelignore           # Exclui venv/tests/backend/frontend do bundle
├── .python-version         # Runtime Python do Vercel (3.12)
├── .env                    # Secrets (never commit)
└── docker-compose.yml      # Postgres (legado — não usado pelo app)
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
- `DATABASE_URL` — URI do SQLAlchemy. Padrão: `sqlite:///contracts.db`. Em
  produção é injetada pela integração Neon; `_normalizar_database_url()` em
  `app/__init__.py` converte `postgres://`/`postgresql://` para
  `postgresql+psycopg://` (driver psycopg 3, exigido pelo SQLAlchemy 2.x).

> O `docker-compose.yml` (Postgres) é legado do protótipo FastAPI e **não** é
> usado nem pelo SQLite local nem pelo Neon em produção.

## Deploy (Vercel)

O app roda em https://contract-generator-lilac.vercel.app. O `vercel.json` usa o
preset `flask`, que detecta o WSGI por `main.py` — **não** existe entrypoint em
`api/` (uma tentativa anterior com `api/index.py` + `rewrites` causou 404 em
todas as rotas, porque o builder monta a função na raiz).

Deploy automático pela integração GitHub: merge na `main` publica em produção,
cada PR gera um preview. Manualmente: `vercel deploy --prod`.

### Implicações do runtime serverless

Filesystem somente-leitura, com `/tmp` efêmero e não compartilhado entre
instâncias. Ao mexer em geração de arquivos ou persistência, respeite:

- **Nada de gravar arquivo para ler depois.** Os DOCX/PDF vivem no banco
  (`ContractRecord.docx_data` / `pdf_data`, `LargeBinary`) e são servidos de
  memória via `BytesIO`. `OUTPUT_DIR` aponta para `/tmp` só como área de
  passagem — o arquivo é lido e removido na mesma requisição.
- Os campos legados `docx_path`/`pdf_path` só atendem registros antigos; use
  as properties `has_docx`/`has_pdf` para checar disponibilidade.
- `_migrar_colunas_de_arquivo()` adiciona as colunas de blob em bancos
  pré-existentes, já que `db.create_all()` não altera tabelas criadas.
- Sem `SECRET_KEY` no ambiente, cada instância gera a sua e as sessões quebram
  de forma intermitente — não só a cada restart.

### De onde vêm as partes

O formulário de contrato não pede mais os dados das partes a cada vez:

- **Contratado** — vive no `User` (colunas `contratado_*`, todas nullable).
  A seção só aparece no formulário enquanto `User.tem_perfil_contratado` é
  falso; o primeiro contrato grava o perfil, e depois disso ele é editado em
  `/account`. `_aplicar_perfil_contratado()` reinjeta os campos no POST.
- **Contratante** — vem da agenda (`Client`), com `<select>` no topo da seção
  preenchendo os campos via `static/js/clients.js`. Os campos continuam
  editáveis: gerar o contrato faz upsert por `(user_id, documento)`, então
  uma correção conserta o cadastro. Sem documento não há upsert.
- Excluir um cliente **não** afeta contratos já gerados — o nome está copiado
  em `ContractRecord.contractor_name`.

`ContractRecord.number` continua `NOT NULL`, mas deixou de ser um input: recebe
um valor derivado (`derivar_numero()` → `isabel-terra-2026-08-21`) que não
aparece em tela nenhuma e serve só para nomear o arquivo baixado.

Colunas adicionadas a tabelas que já existem em produção entram em
`COLUNAS_ADICIONADAS` (`app/__init__.py`) e são aplicadas por
`_migrar_esquema()` no cold start — `db.create_all()` não altera tabela
existente.

### Templates de contrato

Cada tipo é um JSON em `contract_generator/templates/<tipo>.json`, lido por
`models/template.py`. Dois formatos são aceitos:

- **lista de cláusulas** (original — `servico.json`, `locacao.json`);
- **objeto** com `campos` e `clausulas` (`fotografia.json`).

`campos` declara os parâmetros que variam por contrato mas não existem no
formulário padrão — horas contratadas, entrada, prazos, multas. Cada campo
vira um input na seção "Condições do Contrato" (renderizada por
`static/js/contract_fields.js`, que mostra só a do tipo selecionado e
desabilita as demais para não irem no POST) e um placeholder utilizável
pelas cláusulas daquele tipo.

```json
{"nome": "multa_penal", "label": "Multa por descumprimento (%)",
 "tipo": "percentual", "padrao": "25", "ajuda": "...",
 "padrao_de": "contratante_cidade"}
```

- `tipo`: `texto`, `numero`, `inteiro`, `moeda` ou `percentual` — define a
  formatação aplicada antes de entrar no texto (`450` → `R$ 450,00`).
- `padrao`: usado quando o campo vem vazio no POST.
- `padrao_de`: nome de um campo do formulário padrão usado como último
  recurso (ex.: o foro assume a cidade do contratante).

Os valores chegam ao documento via `Contrato(extras={...})`, que
`to_dict()` mescla — os campos do núcleo têm precedência, então um template
não consegue sobrescrever `valor` ou `contratante_nome`.

**Ao criar um tipo novo:** adicione o JSON, o rótulo em `TIPOS_LABEL`
(`generators/base.py`), o rótulo em `ContractRecord.type_label()`
(`app/models.py`) e a `<option>` em `new_contract.html`. Todo placeholder
usado nas cláusulas precisa existir como campo declarado ou como chave de
`Contrato.to_dict()` — há teste cobrindo isso em `tests/test_templates.py`.

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
- `POST /account/contratado` — gravar o perfil de contratado da conta
- `GET/POST /account/password` — trocar senha (exige a senha atual)
- `POST /account/delete` — excluir a própria conta (cascade nos contratos)

`clients_bp` (`app/clients.py`):
- `GET /clientes` — agenda do usuário
- `GET/POST /clientes/<id>/editar`
- `POST /clientes/<id>/excluir` — sai da agenda; o histórico fica intacto

`contracts_bp` (`app/contracts.py`):
- `GET /` — dashboard (lista os contratos do `current_user`)
- `GET/POST /contracts/new` — gerar contrato (DOCX/PDF)
- `GET /contracts/<id>/view` e `/view/pdf` — visualização inline
- `GET /contracts/<id>/download/<fmt>` — download (`docx`/`pdf`), nomeado por
  `ContractRecord.nome_do_arquivo()`
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
