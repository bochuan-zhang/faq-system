from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import openai
import os
from dotenv import load_dotenv
from typing import List
import re
import uuid

from .database import get_db, engine
from .models import Base, Ticket
from .schemas import ChatRequest, ChatResponse, TicketCreate, TicketResponse, FeedbackRequest, FeedbackResponse

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FAQ System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_knowledge_base():
    """Load the knowledge base from knowledge.txt"""
    try:
        with open("knowledge.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Knowledge base not found."

def search_knowledge_base(query: str, knowledge_content: str) -> str:
    """Simple keyword-based search in knowledge base"""
    query_lower = query.lower()
    knowledge_lower = knowledge_content.lower()
    
    # Simple keyword matching
    keywords = query_lower.split()
    relevant_sections = []
    
    # Split knowledge into sections
    sections = knowledge_content.split('\n\n')
    
    for section in sections:
        section_lower = section.lower()
        score = 0
        for keyword in keywords:
            if keyword in section_lower:
                score += 1
        
        if score > 0:
            relevant_sections.append((score, section))
    
    # Sort by relevance score and return top sections
    relevant_sections.sort(key=lambda x: x[0], reverse=True)
    
    if relevant_sections:
        return "\n\n".join([section for score, section in relevant_sections[:3]])
    else:
        return "No relevant information found in knowledge base."

def is_fallback_response(response: str) -> bool:
    """Check if the AI response indicates a fallback"""
    fallback_phrases = [
        "i'm not sure",
        "i don't know",
        "i cannot provide",
        "i'm unable to",
        "i don't have enough information",
        "i'm sorry, but",
        "unfortunately, i",
        "i cannot answer",
        "i don't have access to",
        "i'm not able to"
    ]
    
    response_lower = response.lower()
    return any(phrase in response_lower for phrase in fallback_phrases)

def get_fallback_response(query: str, relevant_content: str) -> str:
    """Provide a fallback response when OpenAI API is unavailable"""
    query_lower = query.lower()
    
    # Simple keyword-based responses
    if any(word in query_lower for word in ['password', 'reset', 'forgot']):
        return "To reset your password, click the 'Forgot Password' link on the login page. Enter your email address, and we'll send you a password reset link. Click the link in the email to create a new password."
    
    elif any(word in query_lower for word in ['account', 'create', 'signup', 'sign up']):
        return "To create an account, visit our website and click the 'Sign Up' button. You'll need to provide your email address, create a password, and verify your email address."
    
    elif any(word in query_lower for word in ['billing', 'payment', 'pay', 'subscription']):
        return "We accept all major credit cards, PayPal, and bank transfers. You can update your billing information in your account settings under Billing > Payment Methods."
    
    elif any(word in query_lower for word in ['upload', 'file', 'document']):
        return "To upload files, click the 'Upload' button in the main interface. You can drag and drop files directly into the upload area or click to browse your computer."
    
    elif any(word in query_lower for word in ['share', 'collaborate', 'permission']):
        return "You can share documents by clicking the 'Share' button on any document. Enter the email addresses of people you want to share with and set their permission level."
    
    elif any(word in query_lower for word in ['support', 'help', 'contact']):
        return "You can contact our support team through multiple channels: Email us at support@company.com, use the live chat feature on our website, or call us at 1-800-SUPPORT during business hours."
    
    elif any(word in query_lower for word in ['mobile', 'app', 'phone']):
        return "Yes, we have mobile apps available for iOS and Android devices. You can download them from the App Store or Google Play Store."
    
    elif any(word in query_lower for word in ['security', 'privacy', 'data']):
        return "We take data security seriously. All data is encrypted in transit and at rest using AES-256 encryption. We use industry-standard security measures and comply with GDPR, HIPAA, and SOC 2 standards."
    
    elif any(word in query_lower for word in ['limit', 'storage', 'quota']):
        return "Free accounts can upload up to 1GB of files. Paid plans offer 10GB, 100GB, and unlimited storage depending on your subscription level."
    
    else:
        # If we have relevant content from knowledge base, use it
        if relevant_content and len(relevant_content) > 50:
            # Extract the most relevant section
            sections = relevant_content.split('\n\n')
            if sections:
                return sections[0]  # Return the first relevant section
        
        return "I'm sorry, but I don't have enough information to answer your question. I've created a support ticket for you, and our team will get back to you soon."

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Handle chat requests with AI-powered responses"""
    try:
        # Generate unique message ID for feedback tracking
        message_id = str(uuid.uuid4())
        
        # Load knowledge base
        knowledge_content = load_knowledge_base()
        
        # Search for relevant content
        relevant_content = search_knowledge_base(request.message, knowledge_content)
        
        # Prepare prompt for OpenAI
        system_prompt = f"""You are a helpful customer support assistant. Use the following knowledge base to answer customer questions. If the knowledge base doesn't contain relevant information, be honest and say you don't have enough information to help.

Knowledge Base:
{relevant_content}

Please provide a helpful, accurate response based on the knowledge base. If you cannot provide a satisfactory answer, indicate this clearly."""
        
        user_prompt = f"Customer question: {request.message}"
        
        # Try to call OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Check if response indicates fallback
            ticket_created = False
            if is_fallback_response(ai_response):
                # Create a ticket
                ticket = Ticket(
                    user_question=request.message,
                    user_contact=request.user_contact
                )
                db.add(ticket)
                db.commit()
                ticket_created = True
                
                # Modify response to indicate ticket creation
                ai_response += "\n\nI've created a support ticket for your question. Our team will get back to you soon."
            
            return ChatResponse(response=ai_response, ticket_created=ticket_created, message_id=message_id)
            
        except Exception as openai_error:
            # If OpenAI API fails, use fallback response
            print(f"OpenAI API error: {openai_error}")
            
            # Get fallback response
            fallback_response = get_fallback_response(request.message, relevant_content)
            
            # Create a ticket for the question since we're using fallback
            ticket = Ticket(
                user_question=request.message,
                user_contact=request.user_contact
            )
            db.add(ticket)
            db.commit()
            
            # Add note about using fallback response
            fallback_response += "\n\nNote: This is a fallback response due to OpenAI API limitations. A support ticket has been created for your question."
            
            return ChatResponse(response=fallback_response, ticket_created=True, message_id=message_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """Handle user feedback on AI responses"""
    try:
        ticket_created = False
        
        # If feedback is negative (not helpful), create a ticket
        if not request.is_helpful:
            # Create a ticket for the unsatisfactory response with the original question
            ticket = Ticket(
                user_question=f"User marked response as unhelpful for question: '{request.original_question}' (Message ID: {request.message_id})",
                user_contact=request.user_contact
            )
            db.add(ticket)
            db.commit()
            ticket_created = True
        
        return FeedbackResponse(success=True, ticket_created=ticket_created)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

@app.post("/ticket", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket"""
    try:
        db_ticket = Ticket(
            user_question=ticket.user_question,
            user_contact=ticket.user_contact
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@app.get("/tickets", response_model=List[TicketResponse])
async def get_tickets(db: Session = Depends(get_db)):
    """Get all tickets"""
    try:
        tickets = db.query(Ticket).order_by(Ticket.timestamp.desc()).all()
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tickets: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "FAQ System API is running"} 