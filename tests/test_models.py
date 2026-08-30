"""Testes das regras de validação dos dados do contrato (issue #14)."""

from datetime import date

import pytest

from contract_generator.models.validators import (
    validar_cpf, validar_cnpj, validar_documento,
    validar_telefone, validar_cep, formatar_telefone, formatar_cep)
from contract_generator.models.party import Parte, Endereco
from contract_generator.models.contract import Contrato
from contract_generator.models.clause import Clausula

# Documentos válidos (dígitos verificadores corretos) usados nos testes.
CPF_VALIDO = "12345678909"
CPF_VALIDO_2 = "98765432100"
CNPJ_VALIDO = "11222333000181"


# --- CPF -------------------------------------------------------------------

@pytest.mark.parametrize("cpf", [
    CPF_VALIDO,
    "123.456.789-09",  # com máscara
    CPF_VALIDO_2,
])
def test_cpf_valido(cpf):
    assert validar_cpf(cpf) is True


@pytest.mark.parametrize("cpf", [
    "111.111.111-11",   # sequência repetida
    "123.456.789-01",   # dígito verificador errado
    "123",              # curto demais
    "abc",              # não numérico
    "",                 # vazio
    "123456789012",     # longo demais
])
def test_cpf_invalido(cpf):
    assert validar_cpf(cpf) is False


# --- CNPJ ------------------------------------------------------------------

@pytest.mark.parametrize("cnpj", [CNPJ_VALIDO, "11.222.333/0001-81"])
def test_cnpj_valido(cnpj):
    assert validar_cnpj(cnpj) is True


@pytest.mark.parametrize("cnpj", [
    "11.222.333/0001-80",  # dígito errado
    "00000000000000",      # sequência repetida
    "123",                 # curto
    "",                    # vazio
])
def test_cnpj_invalido(cnpj):
    assert validar_cnpj(cnpj) is False


def test_validar_documento_respeita_o_tipo():
    assert validar_documento(CPF_VALIDO, "CPF") is True
    assert validar_documento(CPF_VALIDO, "CNPJ") is False
    assert validar_documento(CNPJ_VALIDO, "CNPJ") is True
    assert validar_documento(CNPJ_VALIDO, "outro") is False


# --- Telefone e CEP --------------------------------------------------------

@pytest.mark.parametrize("tel", [
    "11987654321",       # celular com DDD
    "(11) 98765-4321",   # com máscara
    "1133334444",        # fixo com DDD
    "5511987654321",     # com código do país
])
def test_telefone_valido(tel):
    assert validar_telefone(tel) is True


@pytest.mark.parametrize("tel", ["não é telefone", "123", "999999999999999"])
def test_telefone_invalido(tel):
    assert validar_telefone(tel) is False


def test_cep_valido_e_invalido():
    assert validar_cep("88010-000") is True
    assert validar_cep("88010000") is True
    assert validar_cep("123") is False
    assert validar_cep("abcdefgh") is False


def test_formatacao():
    assert formatar_telefone("11987654321") == "(11) 98765-4321"
    assert formatar_telefone("1133334444") == "(11) 3333-4444"
    assert formatar_cep("88010000") == "88010-000"


# --- Parte: validação bloqueante -------------------------------------------

def _parte(**kwargs):
    base = dict(nome="Fulano", documento=CPF_VALIDO, tipo_documento="CPF",
                email="", telefone="")
    base.update(kwargs)
    return Parte(**base)


def test_parte_aceita_dados_validos():
    parte = _parte(telefone="11987654321")
    assert parte.documento_formatado() == "123.456.789-09"
    assert parte.telefone_formatado() == "(11) 98765-4321"


def test_parte_rejeita_cpf_invalido():
    with pytest.raises(ValueError, match="CPF inválido"):
        _parte(documento="12345678901")


def test_parte_rejeita_telefone_invalido():
    with pytest.raises(ValueError, match="Telefone inválido"):
        _parte(telefone="não é telefone")


def test_parte_rejeita_cep_invalido():
    endereco = Endereco(cep="123", logradouro="Rua X", numero="1",
                        complemento="", bairro="Centro", cidade="Floripa",
                        estado="SC")
    with pytest.raises(ValueError, match="CEP inválido"):
        _parte(endereco=endereco)


# --- Contrato: vigência ----------------------------------------------------

def _contrato(data_inicio, data_fim):
    return Contrato(
        tipo="servico", numero="1/2026", data_criacao=date.today(),
        data_inicio=data_inicio, data_fim=data_fim,
        contratante=_parte(nome="A", documento=CPF_VALIDO),
        contratado=_parte(nome="B", documento=CPF_VALIDO_2),
        clausulas=[Clausula(numero=1, titulo="Objeto", conteudo="...")],
        valor=100.0, forma_pagamento="à vista",
    )


def test_contrato_rejeita_vigencia_invertida():
    with pytest.raises(ValueError, match="anterior à data de início"):
        _contrato(date(2026, 12, 1), date(2020, 1, 1))


def test_contrato_aceita_vigencia_valida_e_indeterminada():
    assert _contrato(date(2026, 1, 1), date(2026, 12, 31)) is not None
    assert _contrato(date(2026, 1, 1), None) is not None
