"""Formatação dos valores que entram no texto das cláusulas."""


def formatar_moeda(valor: float) -> str:
    """Formata um número como moeda brasileira: 1234.5 -> 'R$ 1.234,50'."""
    texto = f"R$ {float(valor):,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(valor: float) -> str:
    """Formata um número como percentual: 15 -> '15%'; 12.5 -> '12,5%'."""
    numero = float(valor)
    if numero == int(numero):
        return f"{int(numero)}%"
    return f"{numero:.2f}".rstrip("0").rstrip(".").replace(".", ",") + "%"


MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro")


def data_por_extenso(data) -> str:
    """Formata a data do fecho do contrato: '21 de agosto de 2026'."""
    return f"{data.day} de {MESES[data.month - 1]} de {data.year}"
