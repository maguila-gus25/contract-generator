"""Testes de autenticação, CRUD de usuário e isolamento de dados."""

from app import db
from app.models import User, ContractRecord
from tests.conftest import registrar


def _criar_contrato(app, user_id, number="001/2024"):
    with app.app_context():
        rec = ContractRecord(
            user_id=user_id,
            number=number,
            contract_type="servico",
            contractor_name="Contratante X",
            contracted_name="Contratado Y",
            value=1000.0,
            payment_method="à vista",
            start_date="2024-01-01",
        )
        db.session.add(rec)
        db.session.commit()
        return rec.id


def _criar_usuario(app, email, senha="senha123"):
    with app.app_context():
        user = User(name="Dono", email=email)
        user.set_password(senha)
        db.session.add(user)
        db.session.commit()
        return user.id


# --- Registro / validação de senha ---------------------------------------

def test_registro_autentica_e_acessa_dashboard(client):
    resp = registrar(client)
    assert resp.status_code == 200
    assert "Meus Contratos" in resp.get_data(as_text=True)


def test_registro_rejeita_senha_fraca(client, app):
    resp = client.post("/register", data={
        "name": "Fraco",
        "email": "fraco@exemplo.com",
        "password": "123",
        "confirm_password": "123",
    }, follow_redirects=True)
    assert "pelo menos 8" in resp.get_data(as_text=True)
    with app.app_context():
        assert User.query.filter_by(email="fraco@exemplo.com").first() is None


def test_formulario_de_registro_anuncia_requisitos_da_senha(client):
    html = client.get("/register").get_data(as_text=True)
    # O texto do formulário deve refletir a regra real (8 caracteres), não 6.
    assert "Mínimo 8 caracteres" in html
    assert "Mínimo 6 caracteres" not in html


def test_registro_reporta_todos_os_requisitos_de_senha_de_uma_vez(client):
    """'12345678' falha em 'ter letra'; senha curta sem letra falha em duas."""
    resp = client.post("/register", data={
        "name": "Multi",
        "email": "multi@exemplo.com",
        "password": "1234",
        "confirm_password": "1234",
    }, follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert "pelo menos 8 caracteres" in html
    assert "pelo menos uma letra" in html


def test_registro_repopula_nome_e_email_quando_falha(client):
    resp = client.post("/register", data={
        "name": "Ana Repopula",
        "email": "repopula@exemplo.com",
        "password": "123",
        "confirm_password": "123",
    }, follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert "Ana Repopula" in html
    assert "repopula@exemplo.com" in html


# --- Isolamento entre usuários (IDOR) -------------------------------------

def test_usuario_nao_acessa_contrato_de_outro(client, app):
    dono_id = _criar_usuario(app, "dono@exemplo.com")
    contrato_id = _criar_contrato(app, dono_id)

    # Usuário B se registra/loga e tenta acessar o contrato do dono.
    registrar(client, name="B", email="b@exemplo.com")

    assert client.get(f"/contracts/{contrato_id}/view").status_code == 403
    assert client.get(f"/contracts/{contrato_id}/download/pdf").status_code == 403
    assert client.post(f"/contracts/{contrato_id}/delete").status_code == 403


def test_rotas_de_contrato_exigem_login(client, app):
    dono_id = _criar_usuario(app, "dono2@exemplo.com")
    contrato_id = _criar_contrato(app, dono_id)
    # Sem login: Flask-Login redireciona para a tela de login.
    resp = client.get(f"/contracts/{contrato_id}/view")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


# --- CRUD de usuário (self-service) ---------------------------------------

def test_atualizar_perfil(client, app):
    registrar(client, email="perfil@exemplo.com")
    client.post("/account", data={"name": "Novo Nome", "email": "perfil@exemplo.com"})
    with app.app_context():
        user = User.query.filter_by(email="perfil@exemplo.com").first()
        assert user.name == "Novo Nome"


def test_trocar_senha(client):
    registrar(client, email="senha@exemplo.com", senha="senha123")
    resp = client.post("/account/password", data={
        "current_password": "senha123",
        "new_password": "novasenha1",
        "confirm_password": "novasenha1",
    }, follow_redirects=True)
    assert "sucesso" in resp.get_data(as_text=True).lower()

    client.get("/logout")
    resp = client.post("/login", data={
        "email": "senha@exemplo.com",
        "password": "novasenha1",
    }, follow_redirects=True)
    assert "Meus Contratos" in resp.get_data(as_text=True)


def test_excluir_conta_remove_usuario_e_contratos(client, app):
    registrar(client, email="delete@exemplo.com")
    with app.app_context():
        user = User.query.filter_by(email="delete@exemplo.com").first()
        user_id = user.id
    _criar_contrato(app, user_id, number="999/2024")

    client.post("/account/delete")

    with app.app_context():
        assert User.query.filter_by(email="delete@exemplo.com").first() is None
        assert ContractRecord.query.filter_by(user_id=user_id).count() == 0
