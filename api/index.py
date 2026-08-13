"""Entrypoint WSGI para o runtime Python do Vercel.

O Vercel importa este módulo e procura a variável `app` (aplicação WSGI).
Todo o tráfego é redirecionado para cá pelo `rewrites` do `vercel.json`,
inclusive `/static/...`, que o próprio Flask serve.
"""

import os
import sys

# A raiz do repositório precisa estar no path para importar `app` e
# `contract_generator` — o Vercel executa a função a partir de `api/`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

app = create_app()
