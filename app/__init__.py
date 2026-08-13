import logging
import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Carrega variáveis do arquivo .env (se existir) para o ambiente.
load_dotenv()

logger = logging.getLogger(__name__)

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def _normalizar_database_url(url: str) -> str:
    """Ajusta a URL do Postgres para o driver usado pelo SQLAlchemy 2.x.

    Provedores gerenciados (Neon, Supabase, Heroku) entregam `postgres://`,
    que o SQLAlchemy 2.x não reconhece, e `postgresql://` cai no psycopg2.
    Aqui o driver é o psycopg 3, então normalizamos para `postgresql+psycopg`.
    """
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + url[len(prefixo):]
    return url


def _migrar_colunas_de_arquivo(app) -> None:
    """Adiciona as colunas de blob em bancos criados antes da migração.

    `db.create_all()` só cria tabelas que não existem — não altera as que já
    existem. Sem isso, um `contracts.db` antigo quebraria toda query em
    `ContractRecord` por causa das colunas novas.
    """
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    if "contracts" not in inspector.get_table_names():
        return

    existentes = {col["name"] for col in inspector.get_columns("contracts")}
    faltantes = {"docx_data", "pdf_data"} - existentes
    if not faltantes:
        return

    tipo = "BYTEA" if db.engine.dialect.name == "postgresql" else "BLOB"
    with db.engine.begin() as conn:
        for coluna in sorted(faltantes):
            conn.execute(text(f"ALTER TABLE contracts ADD COLUMN {coluna} {tipo}"))
    logger.info("Colunas adicionadas em `contracts`: %s", ", ".join(sorted(faltantes)))


def create_app(test_config: dict | None = None):
    app = Flask(__name__)

    # SECRET_KEY assina as sessões. Em produção, defina SECRET_KEY no ambiente.
    # Sem ela, geramos uma chave efêmera (invalida sessões a cada reinício) em
    # vez de cair num valor fixo previsível.
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        secret_key = secrets.token_hex(32)
        logger.warning(
            "SECRET_KEY não definida no ambiente; usando chave efêmera. "
            "Defina SECRET_KEY em produção para manter as sessões válidas."
        )
    app.config["SECRET_KEY"] = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = _normalizar_database_url(
        os.environ.get("DATABASE_URL", "sqlite:///contracts.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Em serverless cada instância mantém seu pool; reciclar conexões evita
    # reaproveitar sockets já derrubados pelo Postgres gerenciado.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Persistência do "Lembrar-me" e endurecimento dos cookies de sessão.
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Overrides para testes (ex.: DB em memória, CSRF e rate limit desligados).
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    from .auth import auth_bp
    from .contracts import contracts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(contracts_bp)

    with app.app_context():
        try:
            db.create_all()
            _migrar_colunas_de_arquivo(app)
        except Exception:
            # Uma falha transitória do banco não pode derrubar o processo
            # inteiro no cold start; as rotas devolvem o erro por requisição.
            logger.exception("Falha ao preparar o schema do banco.")

    return app
