# FAQ System - AI-Powered Customer Support

A minimal Customer FAQ System with a FastAPI backend and React frontend that provides AI-powered customer support with automatic ticket creation for unanswered questions.

## Features

- 🤖 **AI-Powered Chat**: Uses OpenAI GPT-3.5-turbo to answer customer questions
- 📚 **Knowledge Base**: Searches through a local knowledge.txt file for relevant information
- 🎫 **Automatic Ticket Creation**: Creates support tickets when AI cannot provide satisfactory answers
- 💬 **Real-time Chat Interface**: Modern React chat interface with typing indicators
- 📋 **Ticket Management**: View and manage all support tickets
- 🎨 **Modern UI**: Clean, responsive design that works on all devices
- 🗄️ **SQLite Database**: Lightweight local database for ticket storage

## Project Structure

```
faq-system/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── database.py      # Database configuration
│   ├── knowledge.txt        # Knowledge base file
│   ├── requirements.txt     # Python dependencies
│   ├── main.py             # Entry point
│   └── README.md           # Backend setup instructions
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.js
│   │   │   └── TicketsView.js
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── README.md           # Frontend setup instructions
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python main.py
```

The backend will run on http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will run on http://localhost:3000

## API Endpoints

### Backend API

- `POST /chat` - Send a message and get AI response
  - Body: `{"message": "string", "user_contact": "string (optional)"}`
  - Response: `{"response": "string", "ticket_created": boolean}`

- `POST /ticket` - Create a support ticket
  - Body: `{"user_question": "string", "user_contact": "string (optional)"}`

- `GET /tickets` - Get all tickets
  - Response: Array of ticket objects

- `GET /` - Health check

## How It Works

1. **User sends a question** through the chat interface
2. **Backend searches** the knowledge.txt file for relevant content using keyword matching
3. **OpenAI API** receives the user question along with relevant knowledge base content
4. **AI generates a response** based on the provided context
5. **Fallback detection** checks if the AI response indicates uncertainty
6. **Ticket creation** automatically occurs if the AI cannot provide a satisfactory answer
7. **Response is sent back** to the user with optional ticket creation notification

## Knowledge Base

The system uses a `knowledge.txt` file containing FAQ content organized by categories:
- Account Management
- Billing and Payments
- Product Features
- Technical Support
- Mobile Access
- Data and Privacy
- Troubleshooting
- Account Limits

## Database Schema

```sql
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    user_question TEXT NOT NULL,
    user_contact VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'open'
);
```

## Customization

### Adding to Knowledge Base
Edit `backend/knowledge.txt` to add more FAQ content. The system uses simple keyword matching, so organize content with clear headings and questions.

### Modifying Fallback Detection
Edit the `is_fallback_response()` function in `backend/app/main.py` to adjust what phrases trigger ticket creation.

### Styling
Modify `frontend/src/App.css` to customize the appearance of the chat interface and ticket view.

## Development

### Backend Development
- FastAPI with automatic API documentation at http://localhost:8000/docs
- SQLAlchemy ORM for database operations
- Pydantic for request/response validation

### Frontend Development
- React 18 with hooks
- React Router for navigation
- Axios for API communication
- Modern CSS with responsive design

## Troubleshooting

### Common Issues

1. **OpenAI API Error**: Make sure your API key is valid and has sufficient credits
2. **Database Error**: The SQLite database will be created automatically on first run
3. **CORS Error**: The backend is configured to allow requests from localhost:3000
4. **Port Conflicts**: Ensure ports 8000 (backend) and 3000 (frontend) are available

### Logs
- Backend logs are displayed in the terminal where you run `python main.py`
- Frontend logs are available in the browser's developer console

## License

This project is for educational and demonstration purposes. Feel free to modify and extend it for your needs. 