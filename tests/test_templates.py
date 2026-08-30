"""Testes dos parâmetros que os templates de contrato declaram."""

import pytest

from contract_generator.models.formatters import (formatar_moeda,
                                                  formatar_percentual)
from contract_generator.models.template import (CampoExtra,
                                                carregar_campos_extras,
                                                ler_template,
                                                listar_tipos_disponiveis)
from contract_generator.models.clause import carregar_clausulas_padrao


def test_tipos_disponiveis_incluem_fotografia():
    assert "fotografia" in listar_tipos_disponiveis()


def test_template_em_formato_lista_continua_funcionando():
    """servico.json é uma lista pura de cláusulas (formato original)."""
    template = ler_template("servico")
    assert template["campos"] == []
    assert len(template["clausulas"]) > 0


def test_template_desconhecido_lista_os_tipos_validos():
    with pytest.raises(FileNotFoundError, match="fotografia"):
        ler_template("inexistente")


def test_fotografia_declara_os_parametros_cobrados():
    nomes = {campo.nome for campo in carregar_campos_extras("fotografia")}
    assert {"duracao_horas", "valor_entrada", "valor_saldo",
            "prazo_entrega_dias", "multa_penal"} <= nomes


def test_todo_placeholder_das_clausulas_tem_campo_ou_e_do_nucleo():
    """Um placeholder sem origem sairia cru no meio do contrato."""
    import re

    nucleo = {"valor", "forma_pagamento", "data_inicio", "data_fim",
              "descricao_servico", "numero", "data_criacao"}
    for tipo in listar_tipos_disponiveis():
        campos = {campo.nome for campo in carregar_campos_extras(tipo)}
        for clausula in carregar_clausulas_padrao(tipo):
            usados = set(re.findall(r"{(\w+)}", clausula.conteudo))
            orfaos = usados - campos - nucleo
            # Os demais placeholders vêm de Contrato.to_dict (partes/endereço).
            assert all(o.startswith(("contratante_", "contratado_"))
                       for o in orfaos), f"{tipo}/{clausula.numero}: {orfaos}"


@pytest.mark.parametrize("tipo, valor, esperado", [
    ("moeda", "450", "R$ 450,00"),
    ("moeda", 1234.5, "R$ 1.234,50"),
    ("percentual", "15", "15%"),
    ("percentual", "12.5", "12,5%"),
    ("inteiro", "20.0", "20"),
    ("texto", "  PIXIESET  ", "PIXIESET"),
    ("numero", "", ""),
])
def test_campo_formata_o_valor_conforme_o_tipo(tipo, valor, esperado):
    campo = CampoExtra(nome="x", label="X", tipo=tipo)
    assert campo.formatar(valor) == esperado


def test_campo_numerico_preserva_texto_invalido():
    """Melhor sair o que o usuário digitou do que engolir o dado."""
    campo = CampoExtra(nome="x", label="X", tipo="moeda")
    assert campo.formatar("a combinar") == "a combinar"


def test_campo_com_tipo_invalido_e_recusado():
    with pytest.raises(ValueError, match="inválido"):
        CampoExtra(nome="x", label="X", tipo="booleano")


def test_formatadores():
    assert formatar_moeda(900) == "R$ 900,00"
    assert formatar_percentual(25) == "25%"


def test_extras_nao_sobrescrevem_campos_do_nucleo():
    from datetime import date
    from contract_generator.models.contract import Contrato
    from contract_generator.models.party import Parte

    parte = Parte("Ana", "12345678909", "CPF", "", "")
    contrato = Contrato(
        tipo="fotografia", numero="1/2026", data_criacao=date(2026, 1, 1),
        data_inicio=date(2026, 1, 1), data_fim=None,
        contratante=parte, contratado=parte,
        clausulas=carregar_clausulas_padrao("fotografia"),
        valor=900.0, forma_pagamento="PIX",
        extras={"valor": "R$ 1,00", "duracao_horas": "3"},
    )
    dados = contrato.to_dict()
    assert dados["valor"] == "R$ 900,00"
    assert dados["duracao_horas"] == "3"


# --- Integração com o formulário -------------------------------------------

import io  # noqa: E402

import docx  # noqa: E402

from .conftest import registrar  # noqa: E402

DADOS_BASE = {
    "contract_type": "fotografia", "number": "7/2026", "value": "900",
    "payment_method": "PIX", "start_date": "2026-08-21", "end_date": "",
    "description": "Ensaio externo",
    "contratante_nome": "Maria", "contratante_tipo_documento": "CPF",
    "contratante_documento": "12345678909", "contratante_cidade": "Florianópolis",
    "contratado_nome": "Ana", "contratado_tipo_documento": "CPF",
    "contratado_documento": "98765432100",
}


def _texto_do_docx(app):
    from app.models import ContractRecord

    with app.app_context():
        record = ContractRecord.query.first()
        documento = docx.Document(io.BytesIO(record.docx_data))
        return "\n".join(p.text for p in documento.paragraphs)


def test_formulario_mostra_os_campos_do_template(client):
    registrar(client)
    pagina = client.get("/contracts/new").get_data(as_text=True)
    assert 'data-tipo="fotografia"' in pagina
    assert 'name="extra_valor_entrada"' in pagina
    assert 'value="PIXIESET"' in pagina  # padrão declarado no template


def test_parametros_informados_chegam_ao_contrato(client, app):
    registrar(client)
    dados = dict(DADOS_BASE, extra_duracao_horas="3", extra_valor_entrada="450",
                 extra_valor_saldo="450", extra_prazo_entrega_dias="15",
                 extra_multa_penal="30", extra_foro_comarca="Curitiba")
    client.post("/contracts/new", data=dados, follow_redirects=True)

    texto = _texto_do_docx(app)
    assert "duração de 3 horas" in texto
    assert "R$ 450,00" in texto
    assert "15 dias úteis" in texto
    assert "multa no valor de 30%" in texto
    assert "comarca de Curitiba" in texto


def test_campos_omitidos_caem_no_padrao_do_template(client, app):
    registrar(client)
    client.post("/contracts/new", data=DADOS_BASE, follow_redirects=True)

    texto = _texto_do_docx(app)
    assert "duração de 2 horas" in texto
    assert "20 dias úteis" in texto
    assert "{" not in texto  # nenhum placeholder cru sobrou


def test_foro_vazio_assume_a_cidade_do_contratante(client, app):
    registrar(client)
    client.post("/contracts/new", data=DADOS_BASE, follow_redirects=True)
    assert "comarca de Florianópolis" in _texto_do_docx(app)


def test_cpf_invalido_no_formulario_nao_gera_contrato(client, app):
    """POST com CPF inválido volta com erro no campo e não salva nada."""
    from app.models import ContractRecord

    registrar(client)
    dados = dict(DADOS_BASE, contratante_documento="12345678901")
    resp = client.post("/contracts/new", data=dados, follow_redirects=True)
    html = resp.get_data(as_text=True)

    assert "CPF inválido" in html
    with app.app_context():
        assert ContractRecord.query.count() == 0


def test_vigencia_invertida_no_formulario_e_reportada(client, app):
    registrar(client)
    dados = dict(DADOS_BASE, start_date="2026-12-01", end_date="2026-01-01")
    resp = client.post("/contracts/new", data=dados, follow_redirects=True)
    assert "anterior à data de início" in resp.get_data(as_text=True)


def test_numero_em_branco_e_gerado_automaticamente(client, app):
    from datetime import date
    from app.models import ContractRecord

    registrar(client)
    dados = dict(DADOS_BASE)
    dados.pop("number")
    client.post("/contracts/new", data=dados, follow_redirects=True)

    with app.app_context():
        registros = ContractRecord.query.all()
        assert len(registros) == 1
        assert registros[0].number == f"001/{date.today().year}"


def test_formulario_sugere_proximo_numero(client, app):
    registrar(client)
    html = client.get("/contracts/new").get_data(as_text=True)
    from datetime import date
    assert f"001/{date.today().year}" in html
