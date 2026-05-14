#!/bin/bash
echo "--- Iniciando o Gerador de Contratos Web ---"

# Cria um novo ambiente virtual se não existir
if [ ! -d "env" ]; then
    echo "Criando novo ambiente virtual (env)..."
    python3 -m venv env
fi

# Ativa o ambiente virtual
source env/bin/activate

# Instala as dependências
echo "Instalando dependências..."
pip install -r ../requirements.txt

# Inicia a API FastAPI em background
echo "Iniciando o servidor da API (FastAPI)..."
python3 -m uvicorn api:app --reload --port 8000 &
API_PID=$!

echo ""
echo "========================================================"
echo "✅ Backend rodando em http://localhost:8000"
echo "✅ Para acessar a interface, abra o arquivo abaixo no seu navegador:"
echo "file://$(pwd)/frontend/index.html"
echo "========================================================"
echo "Pressione CTRL+C para encerrar o servidor."

# Aguarda o processo da API
wait $API_PID
