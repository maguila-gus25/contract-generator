import re


class Endereco:
    def __init__(self, cep: str, logradouro: str, numero: str, complemento: str,
                 bairro: str, cidade: str, estado: str):
        self.cep = cep
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado

    def formatado(self) -> str:
        partes = [f"{self.logradouro}, {self.numero}"]
        if self.complemento:
            partes.append(self.complemento)
        partes.append(f"{self.bairro} - {self.cidade}/{self.estado}")
        partes.append(f"CEP: {self.cep}")
        return ", ".join(partes)

    def __repr__(self) -> str:
        return f"Endereco(cidade={self.cidade!r}, estado={self.estado!r})"


class Parte:
    def __init__(self, nome: str, documento: str, tipo_documento: str,
                 email: str, telefone: str, endereco: Endereco = None):
        self.nome = nome
        self.documento = documento
        self.tipo_documento = tipo_documento.upper()
        self.email = email
        self.telefone = telefone
        self.endereco = endereco
        self.validar()

    def validar(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("Nome da parte deve ser uma string não vazia.")
        if self.tipo_documento not in ("CPF", "CNPJ"):
            raise ValueError("Tipo de documento deve ser 'CPF' ou 'CNPJ'.")
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError(f"E-mail inválido: {self.email}")

    def documento_formatado(self) -> str:
        doc = re.sub(r"\D", "", self.documento)
        if self.tipo_documento == "CPF" and len(doc) == 11:
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        if self.tipo_documento == "CNPJ" and len(doc) == 14:
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
        return self.documento

    def __repr__(self) -> str:
        return f"Parte(nome={self.nome!r}, tipo_documento={self.tipo_documento!r})"
