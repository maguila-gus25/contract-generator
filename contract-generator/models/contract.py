from .party import Parte, Endereco
from .clause import Clausula

class Contrato():
    def __init__(self, titulo: str, contratante: Parte, contratado: Parte, data_hora_criacao: str, valor: float, moeda: str, metodo_pagamento: str, endereco: Endereco):
        self.titulo = titulo
        self.contratante = contratante
        self.contratado = contratado
        self.data_hora_criacao = data_hora_criacao
        self.valor = valor
        self.moeda = moeda
        self.metodo_pagamento = metodo_pagamento
        self.endereco = endereco
        self.clausulas = []
        
    def validar(self):
        if not self.titulo or not str(self.titulo).strip():
            raise ValueError("Título do contrato não pode ser vazio.")
        if not self.contratante:
            raise ValueError("Contratante do contrato não pode ser vazio.")
        if not self.contratado:
            raise ValueError("Contratado do contrato não pode ser vazio.")
        if not self.data_hora_criacao:
            raise ValueError("Data e hora de criação do contrato não pode ser vazio.")
        if self.valor is None or self.valor < 0:
            raise ValueError("Valor do contrato não pode ser vazio ou negativo.")
        if not self.moeda or not str(self.moeda).strip():
            raise ValueError("Moeda do contrato não pode ser vazio.")
        if not self.metodo_pagamento or not str(self.metodo_pagamento).strip():
            raise ValueError("Método de pagamento do contrato não pode ser vazio.")
        if not self.endereco:
            raise ValueError("Endereço do contrato não pode ser vazio.")

    def gerar_texto_completo(self) -> str:
        texto = f"{self.titulo.upper()}\n\n"
        texto += "Por este instrumento particular, de um lado:\n"
        texto += f"{self.contratante.qualificacao()}.\n\n"
        texto += "E de outro lado:\n"
        texto += f"{self.contratado.qualificacao()}.\n\n"
        
        texto += f"Firmam o presente contrato, mediante as cláusulas e condições a seguir:\n\n"
        
        for clausula in self.clausulas:
            texto += f"{clausula.formatada()}\n\n"
            
        texto += "DO VALOR E PAGAMENTO\n"
        texto += f"O valor total do contrato é de {self.moeda} {self.valor:.2f}, pago via {self.metodo_pagamento}.\n\n"
        
        texto += f"E por estarem justos e contratados, assinam o presente contrato.\n\n"
        texto += f"Data de criação: {self.data_hora_criacao}\n\n"
        texto += "__________________________________________________\n"
        texto += f"{self.contratante.name}\n\n"
        texto += "__________________________________________________\n"
        texto += f"{self.contratado.name}\n"
        
        return texto
