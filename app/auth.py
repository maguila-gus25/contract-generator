import os

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db, limiter
from .models import User

auth_bp = Blueprint("auth", __name__)


SENHA_MIN = 8

# Descrição legível das regras, exibida no formulário. Fica ao lado de
# erros_senha() para os dois não voltarem a divergir (ver issue #12).
SENHA_REQUISITOS = (
    f"Mínimo {SENHA_MIN} caracteres, com pelo menos uma letra e um número."
)


def erros_senha(senha: str) -> list[str]:
    """Retorna todos os requisitos de senha não atendidos (vazio se ok)."""
    erros = []
    if len(senha) < SENHA_MIN:
        erros.append(f"A senha deve ter pelo menos {SENHA_MIN} caracteres.")
    if not any(c.isalpha() for c in senha):
        erros.append("A senha deve conter pelo menos uma letra.")
    if not any(c.isdigit() for c in senha):
        erros.append("A senha deve conter pelo menos um número.")
    return erros


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("contracts.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            flash(f"Bem-vindo, {user.name}!", "success")
            return redirect(next_page or url_for("contracts.dashboard"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("contracts.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        erros = erros_senha(password) if password else []
        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
        elif password != confirm:
            flash("As senhas não coincidem.", "danger")
        elif erros:
            for erro in erros:
                flash(erro, "danger")
        elif User.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado.", "danger")
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Conta criada com sucesso!", "success")
            return redirect(url_for("contracts.dashboard"))

        # Mantém nome e e-mail preenchidos quando o cadastro falha.
        return render_template("register.html", name=name, email=email,
                               requisitos_senha=SENHA_REQUISITOS)

    return render_template("register.html", requisitos_senha=SENHA_REQUISITOS)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/account/contratado", methods=["POST"])
@login_required
def account_contratado():
    """Grava o perfil de contratado — os dados de quem presta o serviço.

    Preenchido automaticamente no primeiro contrato; esta rota existe para
    corrigi-lo depois, já que a seção some do formulário assim que existe.
    """
    from .contracts import CAMPOS_CONTRATADO

    nome = request.form.get("contratado_nome", "").strip()
    documento = request.form.get("contratado_documento", "").strip()
    if not nome or not documento:
        flash("Nome e documento do contratado são obrigatórios.", "danger")
        return redirect(url_for("auth.account"))

    for campo in CAMPOS_CONTRATADO:
        valor = request.form.get(f"contratado_{campo}")
        if valor is not None:
            setattr(current_user, f"contratado_{campo}", valor.strip())
    db.session.commit()
    flash("Dados de contratado atualizados.", "success")
    return redirect(url_for("auth.account"))


@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        existente = User.query.filter_by(email=email).first()
        if not name or not email:
            flash("Nome e e-mail são obrigatórios.", "danger")
        elif existente and existente.id != current_user.id:
            flash("Este e-mail já está em uso por outra conta.", "danger")
        else:
            current_user.name = name
            current_user.email = email
            db.session.commit()
            flash("Dados atualizados com sucesso.", "success")
            return redirect(url_for("auth.account"))

    return render_template("account.html")


@auth_bp.route("/account/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        atual = request.form.get("current_password", "")
        nova = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        erros = erros_senha(nova)
        if not current_user.check_password(atual):
            flash("Senha atual incorreta.", "danger")
        elif nova != confirm:
            flash("As senhas não coincidem.", "danger")
        elif erros:
            for erro in erros:
                flash(erro, "danger")
        else:
            current_user.set_password(nova)
            db.session.commit()
            flash("Senha alterada com sucesso.", "success")
            return redirect(url_for("auth.account"))

    return render_template("account_password.html")


@auth_bp.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    user = current_user._get_current_object()

    # Remove os arquivos gerados dos contratos do usuário antes de apagá-lo.
    for contrato in user.contracts:
        for path in (contrato.docx_path, contrato.pdf_path):
            if path and os.path.exists(path):
                os.remove(path)

    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Sua conta e seus contratos foram excluídos.", "info")
    return redirect(url_for("auth.login"))
