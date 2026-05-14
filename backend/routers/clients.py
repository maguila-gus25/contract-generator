from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import models, schemas, auth, database

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

@router.get("", response_model=List[schemas.ClientResponse])
def get_clients(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    return db.query(models.Client).filter(models.Client.user_id == current_user.id).all()

@router.post("", response_model=schemas.ClientResponse)
def create_client(client: schemas.ClientCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_client = models.Client(**client.model_dump(), user_id=current_user.id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_client(client_id: UUID, client: schemas.ClientUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id, models.Client.user_id == current_user.id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: UUID, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id, models.Client.user_id == current_user.id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return None
