from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    user_contact: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    ticket_created: bool = False
    message_id: str  # Add unique ID for tracking feedback

class FeedbackRequest(BaseModel):
    message_id: str
    is_helpful: bool
    user_contact: Optional[str] = None
    original_question: str  # Add the original user question

class FeedbackResponse(BaseModel):
    success: bool
    ticket_created: bool = False

class TicketCreate(BaseModel):
    user_question: str
    user_contact: Optional[str] = None

class TicketResponse(BaseModel):
    id: int
    user_question: str
    user_contact: Optional[str]
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True 