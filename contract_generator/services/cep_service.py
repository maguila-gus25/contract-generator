import re
import requests
from ..models.party import Endereco


class CepService:
    BASE_URL = "https://viacep.com.br/ws/{cep}/json/"
    TIMEOUT = 8

    def buscar(self, cep: str) -> dict:
        cep_limpo = re.sub(r"\D", "", cep)
        if len(cep_limpo) != 8:
            raise ValueError(f"CEP inválido: '{cep}'. Deve ter 8 dígitos numéricos.")

        url = self.BASE_URL.format(cep=cep_limpo)
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise ConnectionError("Tempo esgotado ao consultar o CEP. Verifique sua conexão.")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Sem conexão com a internet. Não foi possível consultar o CEP.")

        dados = response.json()
        if dados.get("erro"):
            raise ValueError(f"CEP '{cep}' não encontrado.")

        return dados

    def buscar_como_endereco(self, cep: str) -> Endereco:
        dados = self.buscar(cep)
        return Endereco(
            cep=dados.get("cep", cep),
            logradouro=dados.get("logradouro", ""),
            numero="",
            complemento=dados.get("complemento", ""),
            bairro=dados.get("bairro", ""),
            cidade=dados.get("localidade", ""),
            estado=dados.get("uf", ""),
        )
