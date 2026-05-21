# contract_generator/generators/__init__.py
# ------------------------------------------------------------
# INICIALIZADOR DO SUBMÓDULO DE GERADORES
#
# O que desenvolver aqui:
#   1. Re-exportar os geradores disponíveis
#      Ex: from contract_generator.generators import DocxGenerator, PdfGenerator
#
#   2. Opcionalmente, criar uma função auxiliar get_generator(formato: str)
#      que recebe "docx" ou "pdf" e retorna o gerador correto.
#      Isso é o padrão de projeto Factory — o main.py não precisa saber
#      qual classe usar, só passa o formato desejado.
# ------------------------------------------------------------
