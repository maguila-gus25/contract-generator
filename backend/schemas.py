from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserSettings(BaseModel):
    settings: Dict[str, Any]

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    settings: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class ClientBase(BaseModel):
    name: Optional[str] = None
    document: Optional[str] = None
    email: Optional[str] = None
    zip_code: Optional[str] = None
    address: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city_state: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ContractBase(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = "Rascunho"
    contractor_data: Optional[Dict[str, Any]] = None
    contractee_data: Optional[Dict[str, Any]] = None
    contract_info: Optional[Dict[str, Any]] = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(ContractBase):
    pass

class ContractStatusUpdate(BaseModel):
    status: str

class ContractResponse(ContractBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HistoryBase(BaseModel):
    action: str
    details: Optional[Dict[str, Any]] = None

class HistoryCreate(HistoryBase):
    contract_id: Optional[UUID] = None

class HistoryResponse(HistoryBase):
    id: UUID
    user_id: UUID
    contract_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
