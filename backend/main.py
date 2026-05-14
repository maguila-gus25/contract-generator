from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta

from . import models, schemas, auth, database
from .routers import users, clients, contracts, history

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Contract Generator API")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(clients.router)
app.include_router(contracts.router)
app.include_router(history.router)

@app.post("/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        settings={"darkMode": True, "accentColor": "#7c3aed", "defaultPayment": "Mensal"}
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# HOW TO RUN:
# 1. Create a virtual environment: python -m venv venv
# 2. Activate it: source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)
# 3. Install dependencies: pip install -r requirements.txt
# 4. Copy .env.example to .env and fill in your values
# 5. Run: uvicorn main:app --reload --port 8000
# 6. Open frontend/index.html in your browser
