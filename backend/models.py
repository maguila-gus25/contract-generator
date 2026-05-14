import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSON, default={})

    clients = relationship("Client", back_populates="owner", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="owner", cascade="all, delete-orphan")
    histories = relationship("History", back_populates="owner", cascade="all, delete-orphan")

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String)
    document = Column(String)
    email = Column(String)
    zip_code = Column(String)
    address = Column(String)
    number = Column(String)
    complement = Column(String)
    neighborhood = Column(String)
    city_state = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="clients")

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String)
    status = Column(String, default="Rascunho")
    contractor_data = Column(JSON)
    contractee_data = Column(JSON)
    contract_info = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="contracts")
    histories = relationship("History", back_populates="contract")

class History(Base):
    __tablename__ = "history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True)
    action = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="histories")
    contract = relationship("Contract", back_populates="histories")
