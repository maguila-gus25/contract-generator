"""Testes da agenda de clientes e do perfil de contratado da conta."""

from app import db
from app.models import Client, ContractRecord, User
from tests.conftest import registrar

DADOS_CONTRATO = {
    "contract_type": "fotografia", "value": "900",
    "payment_method": "PIX", "start_date": "2026-08-21", "end_date": "",
    "description": "Ensaio externo",
    "contratante_nome": "Isabel Terra", "contratante_tipo_documento": "CPF",
    "contratante_documento": "18133602785",
    "contratante_cidade": "Florianópolis",
    "contratado_nome": "Amanda Longhi", "contratado_tipo_documento": "CPF",
    "contratado_documento": "98765432100", "contratado_cidade": "Florianópolis",
}


def _criar_cliente(app, user_id, nome="Cliente X", documento="11122233396"):
    with app.app_context():
        cliente = Client(user_id=user_id, nome=nome, documento=documento,
                         tipo_documento="CPF")
        db.session.add(cliente)
        db.session.commit()
        return cliente.id


def _id_do_usuario(app, email):
    with app.app_context():
        return User.query.filter_by(email=email).first().id


# --- Upsert ao gerar o contrato -------------------------------------------

def test_gerar_contrato_cadastra_o_cliente_na_agenda(client, app):
    registrar(client, email="agenda@exemplo.com")
    client.post("/contracts/new", data=DADOS_CONTRATO, follow_redirects=True)

    with app.app_context():
        cliente = Client.query.filter_by(documento="18133602785").one()
        assert cliente.nome == "Isabel Terra"
        assert cliente.cidade == "Florianópolis"


def test_segundo_contrato_atualiza_o_cliente_em_vez_de_duplicar(client, app):
    registrar(client, email="upsert@exemplo.com")
    client.post("/contracts/new", data=DADOS_CONTRATO, follow_redirects=True)

    corrigido = dict(DADOS_CONTRATO,
                     contratante_nome="Isabel Terra Faillace",
                     contratante_telefone="(48) 99656-5530")
    client.post("/contracts/new", data=corrigido, follow_redirects=True)

    with app.app_context():
        clientes = Client.query.filter_by(documento="18133602785").all()
        assert len(clientes) == 1
        assert clientes[0].nome == "Isabel Terra Faillace"
        assert clientes[0].telefone == "(48) 99656-5530"


def test_cliente_sem_documento_nao_entra_na_agenda(client, app):
    """O documento é a chave de deduplicação — sem ele não há como fazer upsert."""
    registrar(client, email="semdoc@exemplo.com")
    dados = dict(DADOS_CONTRATO, contratante_documento="")
    client.post("/contracts/new", data=dados, follow_redirects=True)

    with app.app_context():
        assert Client.query.count() == 0


def test_excluir_cliente_nao_apaga_o_contrato(client, app):
    registrar(client, email="exclusao@exemplo.com")
    client.post("/contracts/new", data=DADOS_CONTRATO, follow_redirects=True)

    with app.app_context():
        cliente_id = Client.query.one().id

    client.post(f"/clientes/{cliente_id}/excluir", follow_redirects=True)

    with app.app_context():
        assert Client.query.count() == 0
        contrato = ContractRecord.query.one()
        assert contrato.contractor_name == "Isabel Terra"


# --- Isolamento entre usuários --------------------------------------------

def test_usuario_nao_acessa_cliente_de_outro(client, app):
    registrar(client, email="dono-agenda@exemplo.com")
    dono_id = _id_do_usuario(app, "dono-agenda@exemplo.com")
    cliente_id = _criar_cliente(app, dono_id)
    client.get("/logout")

    registrar(client, name="Intruso", email="intruso@exemplo.com")
    assert client.get(f"/clientes/{cliente_id}/editar").status_code == 403
    assert client.post(f"/clientes/{cliente_id}/excluir").status_code == 403


def test_agenda_lista_so_os_proprios_clientes(client, app):
    registrar(client, email="outro-dono@exemplo.com")
    outro_id = _id_do_usuario(app, "outro-dono@exemplo.com")
    _criar_cliente(app, outro_id, nome="Cliente do Outro")
    client.get("/logout")

    registrar(client, name="Eu", email="eu@exemplo.com")
    pagina = client.get("/clientes").get_data(as_text=True)
    assert "Cliente do Outro" not in pagina


def test_editar_cliente_exige_nome_e_documento(client, app):
    registrar(client, email="edicao@exemplo.com")
    user_id = _id_do_usuario(app, "edicao@exemplo.com")
    cliente_id = _criar_cliente(app, user_id, nome="Antes")

    resp = client.post(f"/clientes/{cliente_id}/editar",
                       data={"nome": "", "documento": "11122233396"},
                       follow_redirects=True)
    assert "obrigatórios" in resp.get_data(as_text=True)

    with app.app_context():
        assert db.session.get(Client, cliente_id).nome == "Antes"


# --- Perfil de contratado --------------------------------------------------

def test_primeiro_contrato_grava_o_perfil_de_contratado(client, app):
    registrar(client, email="perfil-contratado@exemplo.com")
    client.post("/contracts/new", data=DADOS_CONTRATO, follow_redirects=True)

    with app.app_context():
        user = User.query.filter_by(email="perfil-contratado@exemplo.com").first()
        assert user.tem_perfil_contratado
        assert user.contratado_nome == "Amanda Longhi"


def test_segundo_contrato_reaproveita_o_perfil_sem_pedir_de_novo(client, app):
    registrar(client, email="reaproveita@exemplo.com")
    client.post("/contracts/new", data=DADOS_CONTRATO, follow_redirects=True)

    # A seção "Contratado" some do formulário assim que o perfil existe.
    pagina = client.get("/contracts/new").get_data(as_text=True)
    assert 'name="contratado_nome"' not in pagina
    assert "Amanda Longhi" in pagina

    # E o POST seguinte, já sem esses campos, sai com o contratado do perfil.
    sem_contratado = {k: v for k, v in DADOS_CONTRATO.items()
                      if not k.startswith("contratado_")}
    client.post("/contracts/new", data=sem_contratado, follow_redirects=True)

    with app.app_context():
        contratos = ContractRecord.query.all()
        assert len(contratos) == 2
        assert all(c.contracted_name == "Amanda Longhi" for c in contratos)


def test_perfil_de_contratado_editavel_na_conta(client, app):
    registrar(client, email="edita-perfil@exemplo.com")
    client.post("/account/contratado", data={
        "contratado_nome": "Amanda Longhi",
        "contratado_documento": "98765432100",
        "contratado_tipo_documento": "CPF",
        "contratado_cidade": "Florianópolis",
    }, follow_redirects=True)

    with app.app_context():
        user = User.query.filter_by(email="edita-perfil@exemplo.com").first()
        assert user.contratado_cidade == "Florianópolis"


# --- Número derivado -------------------------------------------------------

def test_numero_derivado_nomeia_o_arquivo(client, app):
    registrar(client, email="numero@exemplo.com")
    client.post("/contracts/new", data=DADOS_CONTRATO, follow_redirects=True)

    with app.app_context():
        record = ContractRecord.query.one()
        assert record.number == "isabel-terra-2026-08-21"
        assert record.nome_do_arquivo("pdf") == "contrato-isabel-terra-2026-08-21.pdf"


def test_registro_antigo_com_numero_manual_ainda_baixa(app):
    """O número gravado em contratos antigos vira um nome de arquivo válido."""
    with app.app_context():
        record = ContractRecord(number="001/2024", contract_type="servico",
                                contractor_name="X", contracted_name="Y",
                                value=1.0, payment_method="PIX",
                                start_date="2024-01-01", user_id=1)
        assert record.nome_do_arquivo("docx") == "contrato-001-2024.docx"
