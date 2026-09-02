import re

from .validators import (validar_documento, validar_telefone, validar_cep,
                         formatar_telefone, formatar_cep)


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
        partes.append(f"CEP: {formatar_cep(self.cep)}")
        return ", ".join(partes)

    def por_extenso(self) -> str:
        """Endereço em prosa, omitindo o que não foi preenchido.

        Um cadastro incompleto não pode produzir 'Número ,' nem vírgula
        órfã no meio da qualificação da parte.
        """
        partes = []
        if self.logradouro:
            partes.append(self.logradouro)
        if self.numero:
            partes.append(f"Número {self.numero}")
        for campo in (self.complemento, self.bairro, self.cidade):
            if campo:
                partes.append(campo)
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
        if not validar_documento(self.documento, self.tipo_documento):
            raise ValueError(
                f"{self.tipo_documento} inválido: '{self.documento}'."
            )
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError(f"E-mail inválido: {self.email}")
        if self.telefone and not validar_telefone(self.telefone):
            raise ValueError(f"Telefone inválido: '{self.telefone}'.")
        if self.endereco and self.endereco.cep and not validar_cep(self.endereco.cep):
            raise ValueError(f"CEP inválido: '{self.endereco.cep}'.")

    def telefone_formatado(self) -> str:
        return formatar_telefone(self.telefone) if self.telefone else ""

    def qualificacao(self) -> str:
        """A parte em prosa, como aparece na abertura do contrato.

        Cada trecho só entra se houver dado: sem endereço some o domicílio,
        sem telefone e e-mail some o contato.
        """
        texto = f"{self.nome}, {self.tipo_documento} nº {self.documento_formatado()}"

        endereco = self.endereco.por_extenso() if self.endereco else ""
        if endereco:
            texto += f", com domicílio na {endereco}"

        contatos = []
        if self.telefone:
            contatos.append(f"telefone {self.telefone_formatado()}")
        if self.email:
            contatos.append(f"e-mail {self.email}")
        if contatos:
            texto += ", contato pelo " + " e ".join(contatos)

        return texto + "."

    def documento_formatado(self) -> str:
        doc = re.sub(r"\D", "", self.documento)
        if self.tipo_documento == "CPF" and len(doc) == 11:
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        if self.tipo_documento == "CNPJ" and len(doc) == 14:
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
        return self.documento

    def __repr__(self) -> str:
        return f"Parte(nome={self.nome!r}, tipo_documento={self.tipo_documento!r})"
