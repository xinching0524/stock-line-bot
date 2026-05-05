from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api", tags=["donation"])

def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="無效的使用者")
    return user

@router.post("/donation", response_model=schemas.DonationResponse)
def create_donation(donation_req: schemas.DonationRequest, db: Session = Depends(get_db)):
    user = get_user(db, donation_req.username)
    
    new_donation = models.Donation(
        user_id=user.id,
        amount=donation_req.amount,
        message=donation_req.message
    )
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)
    
    return new_donation

@router.get("/donation/history", response_model=List[schemas.DonationResponse])
def get_donations(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return []
    donations = db.query(models.Donation).filter(models.Donation.user_id == user.id).order_by(models.Donation.created_at.desc()).all()
    return donations
