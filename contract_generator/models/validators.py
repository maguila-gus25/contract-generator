"""Validação e formatação dos dados que identificam as partes e a vigência.

Um contrato com CPF inválido é um documento jurídico defeituoso: é o dado
que identifica a parte. Por isso a validação aqui é bloqueante na geração,
e não apenas um aviso (ver issue #14).
"""

import re


def limpar_digitos(valor: str) -> str:
    """Remove tudo que não for dígito."""
    return re.sub(r"\D", "", valor or "")


def validar_cpf(cpf: str) -> bool:
    """Valida um CPF pelos dígitos verificadores.

    Rejeita quantidade de dígitos diferente de 11 e sequências repetidas
    (``000...``, ``111...``), que passam na conta mas nunca são CPFs reais.
    """
    numeros = limpar_digitos(cpf)
    if len(numeros) != 11 or numeros == numeros[0] * 11:
        return False

    for tamanho in (9, 10):
        soma = sum(int(numeros[i]) * (tamanho + 1 - i) for i in range(tamanho))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if digito != int(numeros[tamanho]):
            return False
    return True


def validar_cnpj(cnpj: str) -> bool:
    """Valida um CNPJ pelos dígitos verificadores.

    Rejeita quantidade de dígitos diferente de 14 e sequências repetidas.
    """
    numeros = limpar_digitos(cnpj)
    if len(numeros) != 14 or numeros == numeros[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6] + pesos_1
    for pesos in (pesos_1, pesos_2):
        base = numeros[: len(pesos)]
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if digito != int(numeros[len(pesos)]):
            return False
    return True


def validar_documento(documento: str, tipo_documento: str) -> bool:
    """Valida o documento conforme o tipo declarado ('CPF' ou 'CNPJ')."""
    tipo = (tipo_documento or "").upper()
    if tipo == "CPF":
        return validar_cpf(documento)
    if tipo == "CNPJ":
        return validar_cnpj(documento)
    return False


def validar_telefone(telefone: str) -> bool:
    """Valida um telefone brasileiro: 10 (fixo) ou 11 (celular) dígitos com DDD.

    Aceita o prefixo de país 55. Não valida quando vazio — o campo é opcional;
    a checagem cabe a quem chama.
    """
    numeros = limpar_digitos(telefone)
    if numeros.startswith("55") and len(numeros) in (12, 13):
        numeros = numeros[2:]
    return len(numeros) in (10, 11)


def validar_cep(cep: str) -> bool:
    """Valida o formato de um CEP: 8 dígitos."""
    return len(limpar_digitos(cep)) == 8


def formatar_telefone(telefone: str) -> str:
    """Formata um telefone brasileiro. Devolve o valor cru se não reconhecer."""
    numeros = limpar_digitos(telefone)
    if numeros.startswith("55") and len(numeros) in (12, 13):
        numeros = numeros[2:]
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return telefone


def formatar_cep(cep: str) -> str:
    """Formata um CEP como ``00000-000``. Devolve o valor cru se não reconhecer."""
    numeros = limpar_digitos(cep)
    if len(numeros) == 8:
        return f"{numeros[:5]}-{numeros[5:]}"
    return cep
