# AI Chat Agent (FastAPI + WeatherAPI + MySQL Logging)

A simple AI-style chat agent that:
- Accepts messages via API and a web UI
- Calls an external tool (WeatherAPI.com) when the user types `weather: <city>`
- Logs every conversation turn to MySQL (XAMPP)
- Provides a debug endpoint to fetch logs by session_id

## Features
- **POST /chat**: main chat endpoint
- **GET /logs/{session_id}**: fetch last N logs for a session (debug/testing)
- **GET /**: simple web UI
- **GET /health**: health check

## Tech Stack
- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy + PyMySQL
- MySQL/MariaDB (XAMPP)
- WeatherAPI.com

## Setup

### 1) Create and activate venv
```bash
python -m venv venv
venv\Scripts\activate
