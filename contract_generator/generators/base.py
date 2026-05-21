from abc import ABC, abstractmethod
import os


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
