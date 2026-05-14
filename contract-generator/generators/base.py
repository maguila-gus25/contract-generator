from abc import ABC, abstractmethod
from models.contract import Contrato

class BaseGenerator(ABC):
    @abstractmethod
    def gerar(self, contrato: Contrato, caminho_saida: str):
        pass
