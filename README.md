# Contract Generator

Gerador de contratos jurídicos em formato DOCX e PDF, com interface web, autenticação de usuários e preenchimento automático via API de CEP e CNPJ.

**Aplicação no ar:** https://contract-generator-lilac.vercel.app

---

## Sobre o Projeto

Projeto desenvolvido em Python como parte do portfólio pessoal. O sistema permite que usuários cadastrados gerem contratos de **Prestação de Serviços**, **Locação de Imóvel** e **Produção Fotográfica**, com download nos formatos `.docx` e `.pdf`, de forma simples e rápida via navegador.

---

## Funcionalidades

- Autenticação de usuários (cadastro, login, logout)
- **Gerenciamento de conta:** editar perfil, trocar senha e excluir a própria conta
- Geração de contratos de Prestação de Serviços, Locação de Imóvel e Produção Fotográfica
- Download do contrato nos formatos **.docx** e **.pdf**
- Visualização do PDF inline no navegador
- **Assinatura digital:** botão que baixa o PDF e abre o portal [Assina UFSC](https://assina.ufsc.br) para assinar com certificado ICP-Brasil, gov.br ou idUFSC
- Cláusulas carregadas automaticamente a partir de templates JSON
- **Autocomplete de endereço pelo CEP** (API ViaCEP): ao digitar o CEP, logradouro, bairro, cidade e estado são preenchidos automaticamente
- Consulta de dados de empresa via CNPJ (API ReceitaWS)
- Dashboard com histórico de contratos por usuário
- Exclusão de contratos
- **Segurança:** isolamento de dados entre usuários, proteção CSRF nos formulários e rate limit no login

---

## Tecnologias Utilizadas

| Camada       | Tecnologia              |
|--------------|-------------------------|
| Backend      | Python 3 + Flask        |
| Banco de dados | Flask-SQLAlchemy — SQLite (local) / Postgres (produção) |
| Deploy       | Vercel (serverless) + Neon Postgres |
| Autenticação | Flask-Login + Werkzeug  |
| Segurança    | Flask-WTF (CSRF) + Flask-Limiter (rate limit) |
| Geração DOCX | python-docx             |
| Geração PDF  | fpdf2                   |
| HTTP/APIs    | requests                |
| Frontend     | Bootstrap 5 + Jinja2 + JS vanilla |

---

## Arquitetura — Orientação a Objetos

O projeto é construído em torno de três modelos principais:

```
Parte (party.py)          → Representa contratante ou contratado
  └── Endereco             → Endereço completo da parte

Clausula (clause.py)      → Uma cláusula do contrato
  └── carregar_clausulas_padrao()  → Lê template JSON

Contrato (contract.py)    → Reúne partes, cláusulas e metadados
  ├── validar()            → Verifica integridade dos dados
  └── to_dict()            → Exporta dados para os geradores

GeradorBase (base.py)     → Interface abstrata (SOLID - Open/Closed)
  ├── DocxGenerator        → Implementação Word (.docx)
  └── PdfGenerator         → Implementação PDF (.pdf)
```

---

## Como Instalar

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/contract-generator.git
cd contract-generator

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## Como Usar

```bash
# Inicie o servidor web
python main.py
```

Acesse **http://localhost:5001** no navegador.

> **Nota (macOS):** o app roda na porta **5001** por padrão, porque a porta
> 5000 é ocupada pelo *AirPlay Receiver* do macOS (processo Control Center).
> Para usar outra porta: `PORT=8000 python main.py`.

1. Clique em **Cadastre-se** para criar uma conta
2. Faça login
3. Clique em **Novo Contrato**
4. Preencha os dados do contrato, contratante e contratado — digite o **CEP** e o endereço é preenchido automaticamente
5. Clique em **Gerar Contrato**
6. Baixe o arquivo em **DOCX** ou **PDF**, ou clique em **Assinar no Assina UFSC** na visualização do contrato
7. Gerencie sua conta pelo menu **Minha conta** (perfil, senha e exclusão)

---

## Estrutura do Projeto

```
contract-generator/
│
├── app/                          # Aplicação web Flask
│   ├── __init__.py               # Factory da aplicação
│   ├── auth.py                   # Rotas de autenticação
│   ├── contracts.py              # Rotas de contratos
│   ├── models.py                 # Modelos do banco (User, ContractRecord)
│   ├── templates/                # Templates HTML (Jinja2 + Bootstrap)
│   ├── static/css/style.css      # Estilos customizados
│   └── static/js/cep.js          # Autocomplete de endereço pelo CEP
│
├── contract_generator/           # Biblioteca de geração de contratos
│   ├── models/
│   │   ├── clause.py             # Classe Clausula + loader de templates
│   │   ├── contract.py           # Classe Contrato
│   │   └── party.py              # Classes Parte e Endereco
│   ├── generators/
│   │   ├── base.py               # Classe abstrata GeradorBase
│   │   ├── docx_generator.py     # Gerador de arquivos .docx
│   │   └── pdf_generator.py      # Gerador de arquivos .pdf
│   ├── services/
│   │   ├── cep_service.py        # Consulta de CEP via ViaCEP
│   │   └── cnpj_service.py       # Consulta de CNPJ via ReceitaWS
│   └── templates/
│       ├── servico.json          # Cláusulas do contrato de serviços
│       ├── locacao.json          # Cláusulas do contrato de locação
│       └── fotografia.json       # Cláusulas do contrato de produção fotográfica
│
├── tests/                        # Testes automatizados
├── main.py                       # Ponto de entrada (e entrypoint do Vercel)
├── vercel.json                   # Configuração de deploy (preset Flask)
├── requirements.txt              # Dependências de produção
└── requirements-dev.txt          # Dependências de desenvolvimento
```

---

## Como Rodar os Testes

```bash
pip install -r requirements-dev.txt
pytest
```

---

## Deploy (Vercel)

A aplicação roda em produção no Vercel, com **Neon Postgres** (Marketplace) como
banco. O `vercel.json` usa o preset `flask`, que detecta o app por `main.py` —
não há entrypoint manual em `api/`.

O deploy é automático pela integração com o GitHub:

- merge na `main` → publica em produção;
- cada Pull Request → gera um deploy de preview.

Para publicar manualmente:

```bash
vercel deploy --prod
```

### Variáveis de ambiente

| Variável       | Origem                          | Observação                                    |
|----------------|---------------------------------|-----------------------------------------------|
| `SECRET_KEY`   | definida manualmente            | Sem ela as sessões caem a cada redeploy       |
| `DATABASE_URL` | injetada pela integração Neon   | Chega como `postgres://` e é normalizada no app |

### Restrições do ambiente serverless

O runtime do Vercel tem **filesystem somente-leitura** (só `/tmp`, efêmero e não
compartilhado entre instâncias). Duas consequências no código:

- **Os DOCX/PDF gerados são gravados no banco**, em colunas `LargeBinary`, e
  servidos de memória. Os geradores ainda escrevem em `/tmp`, mas apenas de
  passagem: o arquivo é lido, persistido e removido. Não existe mais uma pasta
  `output/` em produção.
- **SQLite não serve para produção.** O `DATABASE_URL` aponta para o Postgres;
  localmente, sem essa variável, o app continua caindo no `sqlite:///contracts.db`.

Bancos criados antes dessa mudança recebem as colunas novas automaticamente na
inicialização, e registros antigos que apontam para arquivos em disco continuam
sendo lidos.

---

## Aprendizados

- Aplicação de **Orientação a Objetos** com herança, encapsulamento e polimorfismo
- Princípio **Open/Closed (SOLID)**: geradores intercambiáveis sem alterar o código cliente
- **Flask** com Blueprints para separação de responsabilidades
- Autenticação stateful com **Flask-Login** e hash de senha com **Werkzeug**
- ORM com **Flask-SQLAlchemy**, com o mesmo código atendendo SQLite (local) e Postgres (produção)
- **Deploy serverless** na Vercel: adaptar a aplicação a um filesystem somente-leitura e a instâncias sem estado compartilhado
- Geração programática de documentos Word e PDF com bibliotecas Python
- Consumo de APIs REST externas (ViaCEP, ReceitaWS)
- Templates JSON para desacoplar conteúdo jurídico da lógica de programação
- Segurança web: isolamento de dados por usuário, proteção CSRF (Flask-WTF) e rate limit (Flask-Limiter)


## Licença

MIT
