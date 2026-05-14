from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.email is not None:
        current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password")
def change_password(password_update: schemas.UserPasswordUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if not auth.verify_password(password_update.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    current_user.hashed_password = auth.get_password_hash(password_update.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.put("/me/settings")
def update_settings(settings: schemas.UserSettings, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    current_user.settings = settings.settings
    db.commit()
    db.refresh(current_user)
    return current_user.settings
