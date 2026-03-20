# AI Chat Agent

An LLM-powered conversational AI agent built with Python and FastAPI. The agent understands natural language, detects user intent, calls real external APIs, and generates context-aware responses using the Groq LLM API.

## Features

- Natural language understanding via Groq LLM (LLaMA 3.3-70b)
- Intent detection and city extraction through prompt engineering
- Live weather data integration via WeatherAPI
- Full session-based conversation logging to MySQL
- RESTful API built with FastAPI
- Conversation history endpoint

## Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **LLM:** Groq API (LLaMA 3.3-70b-versatile)
- **Database:** MySQL + SQLAlchemy ORM
- **External API:** WeatherAPI
- **Other:** Pydantic, python-dotenv, Uvicorn

## How It Works

1. User sends a natural language message to the API
2. Groq LLM detects intent and extracts relevant data (e.g. city name)
3. Agent calls the appropriate tool (e.g. WeatherAPI)
4. LLM generates a natural, conversational response using the tool result
5. Full conversation is logged to MySQL for session tracking

## Setup

1. Clone the repository
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Create a `.env` file with your credentials:
```
   GROQ_API_KEY=your_groq_api_key
   WEATHER_API_KEY=your_weather_api_key
   DB_HOST=localhost
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=ai_chatbot
```
4. Run the server:
```bash
   uvicorn main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send a message and get AI response |
| GET | `/history/{session_id}` | Get conversation history |

## Example

**Request:**
```json
{
  "message": "What is the weather like in Beirut?",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "response": "It's currently 20°C in Beirut with patchy drizzle. Humidity is at 49% with winds of 49 km/h."
}
```

## Author

Mohamad Khalife — [GitHub](https://github.com/42230772-mk)