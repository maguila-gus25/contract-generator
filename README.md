# Automatizador de Contratos 📄

Este projeto é um gerador automático de contratos desenvolvido em Python. Ele permite a criação rápida de documentos complexos, inserindo automaticamente informações de endereço (via CEP) e dados de empresas (via CNPJ). O sistema gera versões do contrato tanto em PDF quanto em DOCX (Word).

## Estrutura do Projeto

* `models/`: Define as estruturas de dados fundamentais (`Parte`, `Endereco`, `Clausula`, `Contrato`).
* `generators/`: Contém os geradores de documentos responsáveis por transformar o modelo abstrato em arquivos físicos (`PDFGenerator` e `DocxGenerator`).
* `services/`: Serviços de integração com APIs externas (`buscar_cep` usando ViaCEP e `buscar_cnpj` usando BrasilAPI).
* `templates/`: Arquivos JSON com os modelos de cláusulas para cada tipo de contrato (ex: `servico.json`, `locacao.json`).
* `main.py`: O arquivo principal de execução que orquestra todo o processo.

## Setup e Execução

### 1. Requisitos

Certifique-se de ter o **Python 3.8+** instalado em sua máquina.

### 2. Instalação das Dependências

Abra o terminal na pasta do projeto e crie um ambiente virtual para isolar as bibliotecas:

```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
# No Mac/Linux:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instale as bibliotecas
pip install -r requirementes.txt
```

### 3. Executando o Gerador

Com o ambiente virtual ativado, basta rodar o arquivo principal:

```bash
python main.py
```

Você verá o log de execução no terminal informando a busca de dados e a geração dos arquivos.
Ao final, uma nova pasta chamada `output/` será criada contendo os arquivos `contrato.pdf` e `contrato.docx`.

## Bibliotecas Utilizadas

* **requests**: Para fazer a comunicação com as APIs do ViaCEP e BrasilAPI.
* **fpdf2**: Para a geração e formatação avançada de documentos em PDF.
* **python-docx**: Para a criação de documentos compatíveis com o Microsoft Word.
