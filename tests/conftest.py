import pytest

from app import create_app, db


@pytest.fixture
def app(tmp_path):
    """App de teste com banco isolado em arquivo temporário, CSRF e rate
    limit desligados para facilitar os POSTs do test client."""
    db_path = tmp_path / "test.db"
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": False,
    })
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def registrar(client, name="Usuário", email="user@exemplo.com", senha="senha123"):
    """Registra e já autentica um usuário (o /register faz login automático)."""
    return client.post("/register", data={
        "name": name,
        "email": email,
        "password": senha,
        "confirm_password": senha,
    }, follow_redirects=True)
