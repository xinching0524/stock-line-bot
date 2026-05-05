from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., max_length=50)

class UserAuth(UserBase):
    password: str = Field(..., min_length=4)

class DrawRequest(UserBase):
    question: Optional[str] = Field(None, max_length=255)

class PoemResponse(BaseModel):
    id: int
    title: str
    fortune_type: str
    content: str
    explanation: str

    class Config:
        from_attributes = True

class DrawHistoryResponse(BaseModel):
    id: int
    question: Optional[str] = None
    created_at: datetime
    poem: PoemResponse

    class Config:
        from_attributes = True

class DonationRequest(UserBase):
    amount: int
    message: Optional[str] = Field(None, max_length=255)

class DonationResponse(BaseModel):
    id: int
    amount: int
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
