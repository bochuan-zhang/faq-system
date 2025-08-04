from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_question = Column(Text, nullable=False)
    user_contact = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="open") 