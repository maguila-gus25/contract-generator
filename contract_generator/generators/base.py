from abc import ABC, abstractmethod
import os


# Rótulo exibido no título do documento para cada tipo de contrato.
# Deve acompanhar os templates em contract_generator/templates/.
TIPOS_LABEL = {
    "servico": "PRESTAÇÃO DE SERVIÇOS",
    "locacao": "LOCAÇÃO DE IMÓVEL",
    "fotografia": "PRODUÇÃO FOTOGRÁFICA",
}


def rotulo_tipo(tipo: str) -> str:
    """Retorna o rótulo do tipo de contrato para uso no título do documento."""
    return TIPOS_LABEL.get(tipo, tipo.upper())


class GeradorBase(ABC):
    @abstractmethod
    def gerar(self, contrato, caminho_saida: str) -> str:
        pass

    def _preparar_caminho(self, caminho_saida: str, extensao: str) -> str:
        pasta = os.path.dirname(caminho_saida)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        if not caminho_saida.lower().endswith(f".{extensao}"):
            caminho_saida = f"{caminho_saida}.{extensao}"
        return caminho_saida
