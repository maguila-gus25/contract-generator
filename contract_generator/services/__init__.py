# contract_generator/services/__init__.py
# ------------------------------------------------------------
# INICIALIZADOR DO SUBMÓDULO DE SERVIÇOS EXTERNOS
#
# O que desenvolver aqui:
#   1. Re-exportar os serviços disponíveis para facilitar imports
#      Ex: from contract_generator.services import CnpjService, CepService
#
# Contexto:
#   Tudo que envolve comunicação com APIs externas (internet) fica aqui.
#   Isso isola o código de rede do restante da aplicação.
#   Se uma API mudar ou sair do ar, só este módulo precisa ser atualizado.
# ------------------------------------------------------------
