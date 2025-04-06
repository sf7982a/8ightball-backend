from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import models, database
from passlib.hash import bcrypt
from uuid import uuid4
from jose import JWTError, jwt
import datetime

router = APIRouter()

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

class SignUpModel(BaseModel):
    email: str
    password: str
    account_name: str

class LoginModel(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(user: SignUpModel, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    account = models.Account(id=str(uuid4()), name=user.account_name)
    db.add(account)
    db.flush()

    new_user = models.User(
        id=str(uuid4()),
        account_id=account.id,
        email=user.email,
        role="admin",
        password_hash=bcrypt.hash(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"status": "account_created", "user_id": new_user.id, "account_id": account.id}

@router.post("/login")
def login(user: LoginModel, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not bcrypt.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_data = {
        "sub": db_user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "user_id": db_user.id}