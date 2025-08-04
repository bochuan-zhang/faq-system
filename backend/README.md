# FAQ System Backend

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the backend directory with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the server:
```bash
python main.py
```

The server will start on http://localhost:8000

## API Endpoints

- `POST /chat` - Send a message and get AI response
- `POST /ticket` - Create a support ticket
- `GET /tickets` - Get all tickets
- `GET /` - Health check

## Database

The system uses SQLite with SQLAlchemy. The database file `faq_system.db` will be created automatically when you first run the application. 