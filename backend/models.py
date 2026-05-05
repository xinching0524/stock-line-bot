from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Poem(Base):
    __tablename__ = "poems"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    fortune_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)

class DrawHistory(Base):
    __tablename__ = "draw_histories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    poem_id = Column(Integer, ForeignKey("poems.id"), nullable=False)
    question = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User")
    poem = relationship("Poem")

class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    amount = Column(Integer, nullable=False)
    message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
