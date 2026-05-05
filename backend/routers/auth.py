from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/register")
def register(user: schemas.UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="此稱呼已被註冊，請換一個或登入")
    
    new_user = models.User(
        username=user.username,
        password_hash=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "註冊成功"}

@router.post("/login")
def login(user: schemas.UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="稱呼或密碼錯誤")
    
    return {"message": "登入成功", "username": db_user.username}
