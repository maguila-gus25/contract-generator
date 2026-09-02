import io
import os
import tempfile
import uuid
from datetime import date, datetime
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, send_file, abort, jsonify)
from flask_login import login_required, current_user
from . import db
from .clients import salvar_cliente
from .models import Client, ContractRecord

contracts_bp = Blueprint("contracts", __name__)

# Os geradores escrevem em disco, mas o runtime serverless só aceita escrita
# em /tmp — e de forma efêmera. O arquivo é lido de volta e persistido no
# banco logo em seguida; o diretório serve apenas de área de passagem.
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "contract-generator")


def _servir_bytes(dados: bytes, nome: str, mimetype: str, inline: bool = False):
    return send_file(io.BytesIO(dados), mimetype=mimetype,
                     as_attachment=not inline, download_name=nome)


# Os campos declarados pelos templates chegam no POST com este prefixo, para
# não colidirem com os nomes fixos do formulário.
PREFIXO_EXTRA = "extra_"


def _coletar_extras(tipo: str, form_data: dict, carregar_campos) -> dict:
    """Lê os campos que o template do tipo declara e devolve-os formatados.

    Um campo sem valor no POST cai no padrão do template — ou no campo que
    ele indicar em ``padrao_de`` (ex: o foro assume a cidade do contratante).
    Assim uma cláusula nunca fica com o placeholder cru no meio do texto.
    """
    extras = {}
    for campo in carregar_campos(tipo):
        bruto = form_data.get(f"{PREFIXO_EXTRA}{campo.nome}", "")
        if str(bruto).strip() == "":
            bruto = campo.padrao
        if str(bruto).strip() == "" and campo.padrao_de:
            bruto = form_data.get(campo.padrao_de, "")
        extras[campo.nome] = campo.formatar(bruto)
    return extras


# Campos do perfil de contratado, na conta e no formulário (com o prefixo).
CAMPOS_CONTRATADO = ("nome", "documento", "tipo_documento", "email", "telefone",
                     "cep", "logradouro", "numero", "complemento", "bairro",
                     "cidade", "estado")


def _aplicar_perfil_contratado(user, form_data: dict) -> None:
    """Preenche os campos `contratado_*` do POST a partir do perfil da conta.

    A seção "Contratado" só aparece no formulário enquanto a conta não tem
    perfil; a partir daí os dados vêm daqui e o usuário os edita em /account.
    """
    if not user.tem_perfil_contratado:
        return
    for campo in CAMPOS_CONTRATADO:
        form_data[f"contratado_{campo}"] = getattr(user, f"contratado_{campo}") or ""


def _gravar_perfil_contratado(user, form_data: dict) -> None:
    """Grava na conta os dados de contratado digitados no primeiro contrato."""
    if user.tem_perfil_contratado:
        return
    for campo in CAMPOS_CONTRATADO:
        valor = form_data.get(f"contratado_{campo}")
        if valor is not None:
            setattr(user, f"contratado_{campo}", valor.strip())


def _build_contrato(form_data: dict):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from contract_generator.models.party import Parte, Endereco
    from contract_generator.models.contract import Contrato
    from contract_generator.models.clause import carregar_clausulas_padrao
    from contract_generator.models.template import carregar_campos_extras

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
    extras = _coletar_extras(tipo, form_data, carregar_campos_extras)

    data_inicio = datetime.strptime(form_data["start_date"], "%Y-%m-%d").date()
    data_fim_str = form_data.get("end_date", "")
    data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date() if data_fim_str else None

    return Contrato(
        tipo=tipo,
        numero=ContractRecord.derivar_numero(
            form_data["contratante_nome"], form_data["start_date"]
        ),
        data_criacao=date.today(),
        data_inicio=data_inicio,
        data_fim=data_fim,
        contratante=contratante,
        contratado=contratado,
        clausulas=clausulas,
        valor=float(form_data["value"]),
        forma_pagamento=form_data["payment_method"],
        descricao_servico=form_data.get("description", ""),
        extras=extras,
    )


@contracts_bp.route("/")
@login_required
def dashboard():
    contratos = (ContractRecord.query
                 .filter_by(user_id=current_user.id)
                 .order_by(ContractRecord.created_at.desc())
                 .all())
    return render_template("dashboard.html", contratos=contratos)


def _contexto_do_formulario() -> dict:
    """O que o formulário precisa dos templates: campos e descrições padrão."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from contract_generator.models.template import (campos_extras_por_tipo,
                                                    descricao_padrao_por_tipo)

    return {
        "campos_por_tipo": campos_extras_por_tipo(),
        "descricoes_padrao": descricao_padrao_por_tipo(),
    }


def _clientes_do_usuario() -> list:
    """Agenda do usuário, serializada para o seletor de contratante."""
    clientes = (Client.query
                .filter_by(user_id=current_user.id)
                .order_by(Client.nome)
                .all())
    return [cliente.to_dict() for cliente in clientes]


@contracts_bp.route("/contracts/new", methods=["GET", "POST"])
@login_required
def new_contract():
    if request.method == "POST":
        form_data = request.form.to_dict()
        _aplicar_perfil_contratado(current_user, form_data)
        try:
            contrato = _build_contrato(form_data)
        except (ValueError, KeyError) as e:
            flash(f"Erro nos dados do contrato: {e}", "danger")
            return render_template("new_contract.html", form_data=form_data,
                                   clientes=_clientes_do_usuario(),
                                   **_contexto_do_formulario())

        uid = uuid.uuid4().hex[:8]
        base_path = os.path.join(OUTPUT_DIR, f"contrato_{uid}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        def gerar_bytes(gerador, formato: str) -> bytes | None:
            """Gera o arquivo em /tmp, devolve o conteúdo e remove o rastro."""
            caminho = None
            try:
                caminho = gerador.gerar(contrato, base_path)
                with open(caminho, "rb") as arquivo:
                    return arquivo.read()
            except Exception as e:
                flash(f"Erro ao gerar {formato}: {e}", "warning")
                return None
            finally:
                if caminho and os.path.exists(caminho):
                    os.remove(caminho)

        from contract_generator.generators.docx_generator import DocxGenerator
        from contract_generator.generators.pdf_generator import PdfGenerator

        docx_data = gerar_bytes(DocxGenerator(), "DOCX")
        pdf_data = gerar_bytes(PdfGenerator(), "PDF")

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
            docx_data=docx_data,
            pdf_data=pdf_data,
        )
        db.session.add(record)
        # O contrato já saiu: a conta guarda o contratado e a agenda guarda o
        # cliente, para nenhum dos dois voltar a ser digitado.
        _gravar_perfil_contratado(current_user, form_data)
        salvar_cliente(current_user.id, form_data, prefixo="contratante_")
        db.session.commit()

        flash("Contrato gerado com sucesso!", "success")
        return redirect(url_for("contracts.dashboard"))

    return render_template("new_contract.html", form_data={},
                           clientes=_clientes_do_usuario(),
                           **_contexto_do_formulario())


@contracts_bp.route("/api/cep/<cep>")
@login_required
def api_cep(cep: str):
    """Consulta o CEP (ViaCEP) e devolve os campos de endereço em JSON.

    Protegido por login para não servir como proxy aberto à API externa.
    """
    from contract_generator.services.cep_service import CepService

    try:
        endereco = CepService().buscar_como_endereco(cep)
    except ValueError:
        return jsonify({"erro": "CEP não encontrado."}), 404
    except ConnectionError:
        return jsonify({"erro": "Falha ao consultar o CEP."}), 502

    return jsonify({
        "logradouro": endereco.logradouro,
        "bairro": endereco.bairro,
        "cidade": endereco.cidade,
        "estado": endereco.estado,
    })


@contracts_bp.route("/contracts/<int:contract_id>/view")
@login_required
def view_contract(contract_id: int):
    record = ContractRecord.query.get_or_404(contract_id)
    if record.user_id != current_user.id:
        abort(403)

    if not record.has_pdf:
        flash("PDF não disponível para este contrato.", "danger")
        return redirect(url_for("contracts.dashboard"))

    return render_template("view_contract.html", record=record)


@contracts_bp.route("/contracts/<int:contract_id>/view/pdf")
@login_required
def view_pdf(contract_id: int):
    record = ContractRecord.query.get_or_404(contract_id)
    if record.user_id != current_user.id:
        abort(403)

    if record.pdf_data:
        return _servir_bytes(record.pdf_data, record.nome_do_arquivo("pdf"),
                             "application/pdf", inline=True)
    if record.pdf_path and os.path.exists(record.pdf_path):
        return send_file(record.pdf_path, mimetype="application/pdf",
                         as_attachment=False,
                         download_name=record.nome_do_arquivo("pdf"))

    flash("Arquivo não encontrado.", "danger")
    return redirect(url_for("contracts.dashboard"))


@contracts_bp.route("/contracts/<int:contract_id>/download/<fmt>")
@login_required
def download_contract(contract_id: int, fmt: str):
    record = ContractRecord.query.get_or_404(contract_id)
    if record.user_id != current_user.id:
        abort(403)

    DOCX_MIME = ("application/vnd.openxmlformats-officedocument"
                 ".wordprocessingml.document")
    dados, caminho, mimetype = {
        "docx": (record.docx_data, record.docx_path, DOCX_MIME),
        "pdf": (record.pdf_data, record.pdf_path, "application/pdf"),
    }.get(fmt, (None, None, None))

    if dados:
        return _servir_bytes(dados, record.nome_do_arquivo(fmt), mimetype)
    if caminho and os.path.exists(caminho):
        return send_file(caminho, as_attachment=True,
                         download_name=record.nome_do_arquivo(fmt))

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
