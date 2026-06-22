from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    contracts = db.relationship("ContractRecord", backref="owner", lazy=True,
                                cascade="all, delete-orphan")

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
    docx_path = db.Column(db.String(500))
    pdf_path = db.Column(db.String(500))

    def type_label(self) -> str:
        labels = {"servico": "Prestação de Serviços", "locacao": "Locação de Imóvel"}
        return labels.get(self.contract_type, self.contract_type)

    def __repr__(self) -> str:
        return f"<ContractRecord {self.number}>"


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(int(user_id))
