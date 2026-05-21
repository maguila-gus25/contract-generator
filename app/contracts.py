import os
import uuid
from datetime import date, datetime
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, send_file, abort)
from flask_login import login_required, current_user
from . import db
from .models import ContractRecord

contracts_bp = Blueprint("contracts", __name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def _build_contrato(form_data: dict):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from contract_generator.models.party import Parte, Endereco
    from contract_generator.models.contract import Contrato
    from contract_generator.models.clause import carregar_clausulas_padrao

    def make_endereco(prefix):
        cep = form_data.get(f"{prefix}_cep", "")
        if not cep:
            return None
        return Endereco(
            cep=cep,
            logradouro=form_data.get(f"{prefix}_logradouro", ""),
            numero=form_data.get(f"{prefix}_numero", ""),
            complemento=form_data.get(f"{prefix}_complemento", ""),
            bairro=form_data.get(f"{prefix}_bairro", ""),
            cidade=form_data.get(f"{prefix}_cidade", ""),
            estado=form_data.get(f"{prefix}_estado", ""),
        )

    contratante = Parte(
        nome=form_data["contratante_nome"],
        documento=form_data["contratante_documento"],
        tipo_documento=form_data["contratante_tipo_documento"],
        email=form_data.get("contratante_email", ""),
        telefone=form_data.get("contratante_telefone", ""),
        endereco=make_endereco("contratante"),
    )

    contratado = Parte(
        nome=form_data["contratado_nome"],
        documento=form_data["contratado_documento"],
        tipo_documento=form_data["contratado_tipo_documento"],
        email=form_data.get("contratado_email", ""),
        telefone=form_data.get("contratado_telefone", ""),
        endereco=make_endereco("contratado"),
    )

    tipo = form_data["contract_type"]
    clausulas = carregar_clausulas_padrao(tipo)

    data_inicio = datetime.strptime(form_data["start_date"], "%Y-%m-%d").date()
    data_fim_str = form_data.get("end_date", "")
    data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date() if data_fim_str else None

    return Contrato(
        tipo=tipo,
        numero=form_data["number"],
        data_criacao=date.today(),
        data_inicio=data_inicio,
        data_fim=data_fim,
        contratante=contratante,
        contratado=contratado,
        clausulas=clausulas,
        valor=float(form_data["value"]),
        forma_pagamento=form_data["payment_method"],
        descricao_servico=form_data.get("description", ""),
    )


@contracts_bp.route("/")
@login_required
def dashboard():
    contratos = (ContractRecord.query
                 .filter_by(user_id=current_user.id)
                 .order_by(ContractRecord.created_at.desc())
                 .all())
    return render_template("dashboard.html", contratos=contratos)


@contracts_bp.route("/contracts/new", methods=["GET", "POST"])
@login_required
def new_contract():
    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            contrato = _build_contrato(form_data)
        except (ValueError, KeyError) as e:
            flash(f"Erro nos dados do contrato: {e}", "danger")
            return render_template("new_contract.html", form_data=form_data)

        uid = uuid.uuid4().hex[:8]
        base_path = os.path.join(OUTPUT_DIR, f"contrato_{uid}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        docx_path = pdf_path = None
        try:
            from contract_generator.generators.docx_generator import DocxGenerator
            docx_path = DocxGenerator().gerar(contrato, base_path)
        except Exception as e:
            flash(f"Erro ao gerar DOCX: {e}", "warning")

        try:
            from contract_generator.generators.pdf_generator import PdfGenerator
            pdf_path = PdfGenerator().gerar(contrato, base_path)
        except Exception as e:
            flash(f"Erro ao gerar PDF: {e}", "warning")

        record = ContractRecord(
            user_id=current_user.id,
            number=contrato.numero,
            contract_type=contrato.tipo,
            contractor_name=contrato.contratante.nome,
            contracted_name=contrato.contratado.nome,
            value=contrato.valor,
            payment_method=contrato.forma_pagamento,
            start_date=form_data["start_date"],
            end_date=form_data.get("end_date", ""),
            docx_path=docx_path,
            pdf_path=pdf_path,
        )
        db.session.add(record)
        db.session.commit()

        flash(f"Contrato nº {contrato.numero} gerado com sucesso!", "success")
        return redirect(url_for("contracts.dashboard"))

    return render_template("new_contract.html", form_data={})


@contracts_bp.route("/contracts/<int:contract_id>/download/<fmt>")
@login_required
def download_contract(contract_id: int, fmt: str):
    record = ContractRecord.query.get_or_404(contract_id)
    if record.user_id != current_user.id:
        abort(403)

    if fmt == "docx" and record.docx_path and os.path.exists(record.docx_path):
        return send_file(record.docx_path, as_attachment=True,
                         download_name=f"contrato_{record.number}.docx")
    if fmt == "pdf" and record.pdf_path and os.path.exists(record.pdf_path):
        return send_file(record.pdf_path, as_attachment=True,
                         download_name=f"contrato_{record.number}.pdf")

    flash("Arquivo não encontrado.", "danger")
    return redirect(url_for("contracts.dashboard"))


@contracts_bp.route("/contracts/<int:contract_id>/delete", methods=["POST"])
@login_required
def delete_contract(contract_id: int):
    record = ContractRecord.query.get_or_404(contract_id)
    if record.user_id != current_user.id:
        abort(403)

    for path in [record.docx_path, record.pdf_path]:
        if path and os.path.exists(path):
            os.remove(path)

    db.session.delete(record)
    db.session.commit()
    flash("Contrato excluído.", "info")
    return redirect(url_for("contracts.dashboard"))
