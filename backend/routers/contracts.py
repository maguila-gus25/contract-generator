from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import models, schemas, auth, database
from fastapi.responses import FileResponse
import tempfile
import os
from ..services import document_generator
router = APIRouter(
    prefix="/contracts",
    tags=["contracts"]
)

@router.get("", response_model=List[schemas.ContractResponse])
def get_contracts(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    return db.query(models.Contract).filter(models.Contract.user_id == current_user.id).all()

@router.post("", response_model=schemas.ContractResponse)
def create_contract(contract: schemas.ContractCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_contract = models.Contract(**contract.model_dump(), user_id=current_user.id)
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    
    # Add history
    db_history = models.History(
        user_id=current_user.id,
        contract_id=db_contract.id,
        action="created",
        details={"title": db_contract.title}
    )
    db.add(db_history)
    db.commit()
    
    return db_contract

@router.put("/{contract_id}", response_model=schemas.ContractResponse)
def update_contract(contract_id: UUID, contract: schemas.ContractUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    update_data = contract.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_contract, key, value)
    
    db.commit()
    db.refresh(db_contract)
    
    # Add history
    db_history = models.History(
        user_id=current_user.id,
        contract_id=db_contract.id,
        action="updated",
        details={"updates": list(update_data.keys())}
    )
    db.add(db_history)
    db.commit()
    
    return db_contract

@router.patch("/{contract_id}/status", response_model=schemas.ContractResponse)
def update_contract_status(contract_id: UUID, status_update: schemas.ContractStatusUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    db_contract.status = status_update.status
    db.commit()
    db.refresh(db_contract)
    
    # Add history
    db_history = models.History(
        user_id=current_user.id,
        contract_id=db_contract.id,
        action="updated_status",
        details={"status": status_update.status}
    )
    db.add(db_history)
    db.commit()
    
    return db_contract

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: UUID, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    db.delete(db_contract)
    db.commit()
    return None

@router.get("/{contract_id}/download/pdf")
def download_contract_pdf(contract_id: UUID, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file_path = tmp.name
    
    document_generator.generate_pdf(db_contract, file_path)
    
    return FileResponse(path=file_path, filename=f"Contrato_{db_contract.title or 'Gerado'}.pdf", media_type="application/pdf")

@router.get("/{contract_id}/download/docx")
def download_contract_docx(contract_id: UUID, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        file_path = tmp.name
    
    document_generator.generate_docx(db_contract, file_path)
    
    return FileResponse(path=file_path, filename=f"Contrato_{db_contract.title or 'Gerado'}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
