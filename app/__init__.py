import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Carrega variáveis do arquivo .env (se existir) para o ambiente.
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Configuração vinda do ambiente, com defaults seguros para o dev local.
    # SECRET_KEY mantém as sessões válidas entre reinícios — defina no .env em produção.
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///contracts.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Persistência do "Lembrar-me" e endurecimento dos cookies de sessão.
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    from .auth import auth_bp
    from .contracts import contracts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(contracts_bp)

    with app.app_context():
        db.create_all()

    return app
