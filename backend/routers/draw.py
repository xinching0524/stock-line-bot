from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api", tags=["draw"])

def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="無效的使用者")
    return user

@router.post("/draw", response_model=schemas.DrawHistoryResponse)
def create_draw(draw_req: schemas.DrawRequest, db: Session = Depends(get_db)):
    user = get_user(db, draw_req.username)
    
    # 隨機抽取籤詩
    poems = db.query(models.Poem).all()
    if not poems:
        raise HTTPException(status_code=500, detail="Database empty. Run seed.py first.")
    selected_poem = random.choice(poems)
    
    # 儲存抽籤紀錄
    new_history = models.DrawHistory(
        user_id=user.id,
        poem_id=selected_poem.id,
        question=draw_req.question
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    
    return new_history

@router.get("/history", response_model=List[schemas.DrawHistoryResponse])
def get_history(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return []
    history = db.query(models.DrawHistory).filter(models.DrawHistory.user_id == user.id).order_by(models.DrawHistory.created_at.desc()).all()
    return history
