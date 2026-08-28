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
