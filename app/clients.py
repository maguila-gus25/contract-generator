"""Agenda de clientes — o contratante deixa de ser digitado a cada contrato.

Um cliente entra na agenda sozinho quando um contrato é gerado (upsert por
documento, em `contracts.new_contract`); estas rotas existem para revisar,
corrigir e remover o que já está lá.
"""

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from . import db
from .models import Client

clients_bp = Blueprint("clients", __name__)


def _do_usuario(client_id: int) -> Client:
    """Busca o cliente garantindo que ele pertence ao usuário logado."""
    cliente = Client.query.get_or_404(client_id)
    if cliente.user_id != current_user.id:
        abort(403)
    return cliente


def aplicar_dados(cliente: Client, dados: dict, prefixo: str = "") -> None:
    """Copia os campos de um dicionário de formulário para o cliente.

    O `prefixo` atende o formulário de contrato, onde os mesmos campos vêm
    como `contratante_nome`, `contratante_cep` etc.
    """
    for campo in Client.CAMPOS:
        valor = dados.get(f"{prefixo}{campo}")
        if valor is not None:
            setattr(cliente, campo, valor.strip())


def salvar_cliente(user_id: int, dados: dict, prefixo: str = "") -> Client | None:
    """Cria ou atualiza o cliente identificado por `(user_id, documento)`.

    O documento é a chave de deduplicação: sem ele não há como saber se a
    pessoa já está na agenda, então o cliente simplesmente não é salvo.
    """
    documento = (dados.get(f"{prefixo}documento") or "").strip()
    nome = (dados.get(f"{prefixo}nome") or "").strip()
    if not documento or not nome:
        return None

    cliente = Client.query.filter_by(user_id=user_id, documento=documento).first()
    if cliente is None:
        cliente = Client(user_id=user_id, nome=nome, documento=documento)
        db.session.add(cliente)
    aplicar_dados(cliente, dados, prefixo)
    return cliente


@clients_bp.route("/clientes")
@login_required
def listar():
    clientes = (Client.query
                .filter_by(user_id=current_user.id)
                .order_by(Client.nome)
                .all())
    return render_template("clients.html", clientes=clientes)


@clients_bp.route("/clientes/<int:client_id>/editar", methods=["GET", "POST"])
@login_required
def editar(client_id: int):
    cliente = _do_usuario(client_id)

    if request.method == "POST":
        dados = request.form.to_dict()
        nome = (dados.get("nome") or "").strip()
        documento = (dados.get("documento") or "").strip()
        duplicado = (Client.query
                     .filter_by(user_id=current_user.id, documento=documento)
                     .first())

        if not nome or not documento:
            flash("Nome e documento são obrigatórios.", "danger")
        elif duplicado and duplicado.id != cliente.id:
            flash("Já existe um cliente com este documento.", "danger")
        else:
            aplicar_dados(cliente, dados)
            db.session.commit()
            flash("Cliente atualizado.", "success")
            return redirect(url_for("clients.listar"))

    return render_template("client_form.html", cliente=cliente)


@clients_bp.route("/clientes/<int:client_id>/excluir", methods=["POST"])
@login_required
def excluir(client_id: int):
    cliente = _do_usuario(client_id)
    # Os contratos já gerados não são tocados: o nome do contratante está
    # copiado como texto em `ContractRecord.contractor_name`.
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente removido da agenda.", "info")
    return redirect(url_for("clients.listar"))
