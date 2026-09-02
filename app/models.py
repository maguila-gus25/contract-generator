import re
import unicodedata
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


def slug(texto: str) -> str:
    """Reduz um texto a letras, números e hífens: 'Isabel Terra' -> 'isabel-terra'."""
    sem_acento = (unicodedata.normalize("NFKD", texto or "")
                  .encode("ascii", "ignore").decode("ascii"))
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", sem_acento.lower())).strip("-")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    contracts = db.relationship("ContractRecord", backref="owner", lazy=True,
                                cascade="all, delete-orphan")
    clients = db.relationship("Client", backref="owner", lazy=True,
                              cascade="all, delete-orphan")

    # Perfil de contratado: os dados de quem presta o serviço saem do
    # formulário de contrato e passam a viver na conta. Preenchidos no
    # primeiro contrato e editáveis em /account.
    contratado_nome = db.Column(db.String(200))
    contratado_documento = db.Column(db.String(30))
    contratado_tipo_documento = db.Column(db.String(4))
    contratado_email = db.Column(db.String(120))
    contratado_telefone = db.Column(db.String(30))
    contratado_cep = db.Column(db.String(10))
    contratado_logradouro = db.Column(db.String(200))
    contratado_numero = db.Column(db.String(20))
    contratado_complemento = db.Column(db.String(100))
    contratado_bairro = db.Column(db.String(100))
    contratado_cidade = db.Column(db.String(100))
    contratado_estado = db.Column(db.String(2))

    @property
    def tem_perfil_contratado(self) -> bool:
        """Nome e documento bastam para o contrato dispensar a seção."""
        return bool(self.contratado_nome and self.contratado_documento)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class ContractRecord(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    number = db.Column(db.String(50), nullable=False)
    contract_type = db.Column(db.String(50), nullable=False)
    contractor_name = db.Column(db.String(200), nullable=False)
    contracted_name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Os arquivos gerados ficam no próprio banco: o filesystem do runtime
    # serverless é somente-leitura (e o /tmp não é compartilhado entre
    # instâncias), então não há onde guardá-los em disco.
    docx_data = db.Column(db.LargeBinary)
    pdf_data = db.Column(db.LargeBinary)
    # Legado: registros criados antes da migração para blobs apontam para
    # arquivos em disco. Mantidos para leitura no ambiente local.
    docx_path = db.Column(db.String(500))
    pdf_path = db.Column(db.String(500))

    @property
    def has_docx(self) -> bool:
        return bool(self.docx_data or self.docx_path)

    @property
    def has_pdf(self) -> bool:
        return bool(self.pdf_data or self.pdf_path)

    @staticmethod
    def derivar_numero(nome_contratante: str, data_inicio: str) -> str:
        """Identificador interno do registro: 'isabel-terra-2026-08-21'.

        O número deixou de ser um input — a coluna continua `NOT NULL`, mas
        o valor é derivado e nunca exibido. Serve só para nomear o arquivo.
        """
        partes = [p for p in (slug(nome_contratante), slug(data_inicio)) if p]
        return "-".join(partes) or "contrato"

    def nome_do_arquivo(self, fmt: str) -> str:
        """Nome do arquivo servido no download: 'contrato-isabel-terra-2026-08-21.pdf'."""
        return f"contrato-{slug(self.number) or self.id}.{fmt}"

    def type_label(self) -> str:
        labels = {
            "servico": "Prestação de Serviços",
            "locacao": "Locação de Imóvel",
            "fotografia": "Produção Fotográfica",
        }
        return labels.get(self.contract_type, self.contract_type)

    def __repr__(self) -> str:
        return f"<ContractRecord {self.number}>"


class Client(db.Model):
    """Cliente na agenda do usuário — o contratante de contratos futuros.

    O documento é a chave de deduplicação: gerar um contrato faz upsert por
    ``(user_id, documento)``. Excluir um cliente não toca no histórico, já
    que ``ContractRecord.contractor_name`` guarda o nome como texto.
    """

    __tablename__ = "clients"
    __table_args__ = (
        db.UniqueConstraint("user_id", "documento", name="uq_client_user_documento"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    documento = db.Column(db.String(30), nullable=False)
    tipo_documento = db.Column(db.String(4), nullable=False, default="CPF")
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(30))
    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Campos preenchidos pelo formulário de contrato (sem o prefixo da parte).
    CAMPOS = ("nome", "documento", "tipo_documento", "email", "telefone",
              "cep", "logradouro", "numero", "complemento", "bairro",
              "cidade", "estado")

    def to_dict(self) -> dict:
        """Serialização usada pelo seletor de clientes no formulário."""
        dados = {campo: getattr(self, campo) or "" for campo in self.CAMPOS}
        dados["id"] = self.id
        return dados

    def __repr__(self) -> str:
        return f"<Client {self.nome}>"


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(int(user_id))
