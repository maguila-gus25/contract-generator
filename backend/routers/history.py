from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import models, schemas, auth, database

router = APIRouter(
    prefix="/history",
    tags=["history"]
)

@router.get("", response_model=List[schemas.HistoryResponse])
def get_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    return db.query(models.History).filter(models.History.user_id == current_user.id).order_by(models.History.created_at.desc()).all()

@router.get("/{contract_id}", response_model=List[schemas.HistoryResponse])
def get_contract_history(contract_id: UUID, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Verify contract belongs to user
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    return db.query(models.History).filter(models.History.contract_id == contract_id, models.History.user_id == current_user.id).order_by(models.History.created_at.desc()).all()

@router.post("", response_model=schemas.HistoryResponse)
def create_history(history: schemas.HistoryCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if history.contract_id:
        contract = db.query(models.Contract).filter(models.Contract.id == history.contract_id, models.Contract.user_id == current_user.id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
            
    db_history = models.History(**history.model_dump(), user_id=current_user.id)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history
