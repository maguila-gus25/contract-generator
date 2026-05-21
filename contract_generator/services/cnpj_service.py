import re
import requests
from ..models.party import Parte, Endereco


class CnpjService:
    BASE_URL = "https://receitaws.com.br/v1/cnpj/{cnpj}"
    TIMEOUT = 10

    def buscar(self, cnpj: str) -> dict:
        cnpj_limpo = re.sub(r"\D", "", cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError(f"CNPJ inválido: '{cnpj}'. Deve ter 14 dígitos numéricos.")

        url = self.BASE_URL.format(cnpj=cnpj_limpo)
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise ConnectionError("Tempo esgotado ao consultar o CNPJ.")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Sem conexão com a internet ao consultar o CNPJ.")

        dados = response.json()
        if dados.get("status") == "ERROR":
            raise ValueError(f"CNPJ '{cnpj}' não encontrado ou inválido.")

        return dados

    def buscar_como_parte(self, cnpj: str) -> Parte:
        dados = self.buscar(cnpj)
        endereco = Endereco(
            cep=dados.get("cep", ""),
            logradouro=dados.get("logradouro", ""),
            numero=dados.get("numero", ""),
            complemento=dados.get("complemento", ""),
            bairro=dados.get("bairro", ""),
            cidade=dados.get("municipio", ""),
            estado=dados.get("uf", ""),
        )
        return Parte(
            nome=dados.get("nome", ""),
            documento=cnpj,
            tipo_documento="CNPJ",
            email=dados.get("email", ""),
            telefone=dados.get("telefone", ""),
            endereco=endereco,
        )
