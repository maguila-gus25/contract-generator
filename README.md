# Automatizador de Contratos 📄

Este projeto é um sistema web completo (Full-Stack) para automação e geração de contratos jurídicos e de prestação de serviços. Ele possibilita o preenchimento ágil de documentos complexos através de consultas automatizadas (CEP e CNPJ), com persistência de dados e geração de arquivos finais nos formatos **PDF** e **DOCX (Word)**.

Recentemente, o projeto evoluiu para uma arquitetura moderna utilizando **FastAPI** e **PostgreSQL**, agregando suporte a contas de usuários, histórico de contratos e integração com a **Assinatura Digital Gov.br**.

## 🛠️ Funcionalidades Principais

- **Geração de Documentos**: Criação automática de contratos em PDF (via `fpdf2`) e DOCX (via `python-docx`).
- **Preenchimento Automático**: Integração com ViaCEP e BrasilAPI para buscar endereços e dados de empresas (CNPJ) instantaneamente.
- **Autenticação e Gestão de Usuários**: Sistema de login seguro com JWT, e armazenamento de preferências (como Dark Mode).
- **Gestão de Clientes e Contratos**: Banco de dados relacional para gerenciar clientes cadastrados e o histórico de contratos gerados.
- **Assinatura Digital (Gov.br)**: Fluxo de autenticação OAuth 2.0 integrado com SERPRO/ITI para assinatura digital de contratos gerados.

## 📁 Estrutura do Projeto

O repositório é dividido nas seguintes pastas principais:

- `frontend/`: Interface de usuário construída em HTML, CSS (Vanilla) e JavaScript. Comunica-se com as APIs em plano de fundo.
- `backend/`: A nova API RESTFull desenvolvida em **FastAPI** com uso do **SQLAlchemy** para mapeamento objeto-relacional com **PostgreSQL**. Contém as rotas de autenticação, usuários, contratos e histórico.
- `contract-generator/`: O core/motor da geração de documentos. Inclui:
  - `models/`: Estruturas de dados dos contratos (`Parte`, `Endereco`, `Contrato`, etc.).
  - `generators/`: Lógica de exportação dos arquivos físicos (PDF e DOCX).
  - `services/`: Comunicação com APIs externas (CEP e CNPJ).

## 🚀 Setup e Execução (Passo a Passo)

Siga as instruções abaixo para preparar o ambiente e rodar o projeto localmente.

### 1. Pré-requisitos

- **Python 3.10+** instalado.
- **PostgreSQL** instalado e rodando em sua máquina (ou servidor remoto).
- Git.

### 2. Clonando o Repositório

```bash
git clone https://github.com/maguila-gus25/contract-generator.git
cd contract-generator
```

### 3. Configurando o Ambiente Virtual e Dependências

É recomendado isolar as dependências do projeto usando um ambiente virtual.

```bash
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Mac/Linux:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instale todas as dependências
pip install -r requirements.txt
```

### 4. Configuração de Variáveis de Ambiente e Banco de Dados

1. Crie um banco de dados no seu PostgreSQL (ex: `contract_generator_db`).
2. Faça uma cópia do arquivo de configuração de exemplo:
   ```bash
   cp .env.example .env
   ```
3. Abra o arquivo `.env` e preencha a URL do banco de dados e outras chaves necessárias:
   ```env
   # Exemplo: postgresql://postgres:suasenha@localhost:5432/contract_generator_db
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
   SECRET_KEY=sua_chave_super_secreta
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   # Opcional (para assinatura digital Gov.br)
   GOVBR_CLIENT_ID=seu_client_id
   GOVBR_CLIENT_SECRET=seu_client_secret
   GOVBR_REDIRECT_URI=http://localhost/auth/govbr/callback
   GOVBR_ENVIRONMENT=staging
   ```

*Nota: O FastAPI e o SQLAlchemy (configurados no `backend/main.py`) vão criar as tabelas no banco automaticamente na primeira execução.*

### 5. Executando o Backend (API)

O sistema possui a nova API e o motor legado. Para rodar a arquitetura Full-Stack:

```bash
# Certifique-se de que o venv está ativado
# Suba a API FastAPI
uvicorn backend.main:app --reload --port 8000
```
> O backend estará rodando em `http://localhost:8000`. A documentação Swagger poderá ser acessada em `http://localhost:8000/docs`.

*(Alternativa: Caso deseje rodar a API de geração legada original, você pode utilizar o script `./contract-generator/run.sh` ou executar `uvicorn contract-generator.api:app --reload --port 8000`)*

### 6. Executando o Frontend

O frontend não necessita de build ou ferramentas Node.js. Basta abrir o arquivo principal no navegador:

**Opção 1:** Clique duas vezes no arquivo `frontend/index.html` ou abra-o diretamente no navegador (`file:///caminho_do_projeto/frontend/index.html`).

**Opção 2 (Recomendada):** Use uma extensão como o *Live Server* do VS Code para servir o HTML e evitar possíveis bloqueios de CORS, acessando via `http://127.0.0.1:5500/frontend/index.html`.

## 📚 Tecnologias Utilizadas

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, Passlib, Uvicorn, PostgreSQL.
- **Geração de Documentos:** `fpdf2` (PDF) e `python-docx` (Word/DOCX).
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla).
- **Integrações:** ViaCEP, BrasilAPI (CNPJ) e Gov.br (Assinaturas).
