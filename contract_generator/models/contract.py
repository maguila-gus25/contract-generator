from datetime import date
from .party import Parte
from .clause import Clausula


class Contrato:
    def __init__(self, tipo: str, numero: str, data_criacao: date,
                 data_inicio: date, data_fim: date,
                 contratante: Parte, contratado: Parte,
                 clausulas: list, valor: float, forma_pagamento: str,
                 descricao_servico: str = "", observacoes: str = ""):
        self.tipo = tipo
        self.numero = numero
        self.data_criacao = data_criacao
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.contratante = contratante
        self.contratado = contratado
        self.clausulas = clausulas
        self.valor = valor
        self.forma_pagamento = forma_pagamento
        self.descricao_servico = descricao_servico
        self.observacoes = observacoes
        self.validar()

    def validar(self) -> None:
        if not self.tipo or not self.tipo.strip():
            raise ValueError("Tipo do contrato é obrigatório.")
        if not self.numero or not self.numero.strip():
            raise ValueError("Número do contrato é obrigatório.")
        if not isinstance(self.contratante, Parte):
            raise ValueError("Contratante deve ser uma instância de Parte.")
        if not isinstance(self.contratado, Parte):
            raise ValueError("Contratado deve ser uma instância de Parte.")
        if self.valor < 0:
            raise ValueError("Valor do contrato não pode ser negativo.")
        if not self.clausulas:
            raise ValueError("O contrato deve ter pelo menos uma cláusula.")

    def to_dict(self) -> dict:
        end_contratante = self.contratante.endereco.formatado() if self.contratante.endereco else ""
        end_contratado = self.contratado.endereco.formatado() if self.contratado.endereco else ""
        valor_fmt = f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return {
            "tipo": self.tipo,
            "numero": self.numero,
            "data_criacao": self.data_criacao.strftime("%d/%m/%Y"),
            "data_inicio": self.data_inicio.strftime("%d/%m/%Y"),
            "data_fim": self.data_fim.strftime("%d/%m/%Y") if self.data_fim else "Indeterminado",
            "contratante_nome": self.contratante.nome,
            "contratante_documento": self.contratante.documento_formatado(),
            "contratante_tipo_documento": self.contratante.tipo_documento,
            "contratante_email": self.contratante.email,
            "contratante_telefone": self.contratante.telefone,
            "contratante_endereco": end_contratante,
            "contratado_nome": self.contratado.nome,
            "contratado_documento": self.contratado.documento_formatado(),
            "contratado_tipo_documento": self.contratado.tipo_documento,
            "contratado_email": self.contratado.email,
            "contratado_telefone": self.contratado.telefone,
            "contratado_endereco": end_contratado,
            "valor": valor_fmt,
            "forma_pagamento": self.forma_pagamento,
            "descricao_servico": self.descricao_servico,
            "observacoes": self.observacoes,
        }

    def __repr__(self) -> str:
        return f"Contrato(numero={self.numero!r}, tipo={self.tipo!r})"
