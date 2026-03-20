import logging
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Query

from database import get_db, engine, Base
from models import ChatLog
from weather_service import get_current_weather
from claude_service import get_claude_reply

Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

# Keywords that trigger weather lookup (single source of truth)
WEATHER_KEYWORDS = ["weather", "temperature", "forecast", "hot", "cold", "rain"]

app = FastAPI(title="AI Chat Agent (Claude + Weather Tool + DB Logging)")


@app.exception_handler(HTTPException)
def http_exception_handler(_request: Request, exc: HTTPException):
    """Ensure HTTP exceptions return consistent JSON (FastAPI default is already JSON)."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions, log them, and return a safe 500 response."""
    logger.exception("Unhandled exception for %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."},
    )


@app.get("/", response_class=HTMLResponse)
def home():
    index_path = Path(__file__).parent / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return index_path.read_text(encoding="utf-8")

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    message: str = Field(..., min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    session_id: str
    reply: str


class LogEntryResponse(BaseModel):
    id: int
    session_id: str
    user_message: str
    assistant_message: str
    created_at: str | None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    text = req.message.strip()

    try:
        # Detect weather intent by keyword
        if any(word in text.lower() for word in WEATHER_KEYWORDS):
            location_prompt = f"Extract only the city name from this message, nothing else: '{text}'"
            location = get_claude_reply(location_prompt).strip()
            weather_data = get_current_weather(location)
            reply = get_claude_reply(text, weather_result=weather_data)
        else:
            reply = get_claude_reply(text)
    except Exception as e:
        logger.exception("Chat/LLM or weather call failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later.",
        ) from e

    try:
        log = ChatLog(
            session_id=req.session_id,
            user_message=req.message,
            assistant_message=reply,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Failed to persist chat log: %s", e)
        raise HTTPException(
            status_code=503,
            detail="Could not save conversation. Please try again.",
        ) from e

    return ChatResponse(session_id=req.session_id, reply=reply)

@app.get("/logs/{session_id}", response_model=list[LogEntryResponse])
def get_logs(session_id: str, limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    try:
        rows = (
            db.query(ChatLog)
            .filter(ChatLog.session_id == session_id)
            .order_by(ChatLog.id.desc())
            .limit(limit)
            .all()
        )
    except Exception as e:
        logger.exception("Failed to fetch logs for session %s: %s", session_id, e)
        raise HTTPException(
            status_code=503,
            detail="Could not load conversation history. Please try again.",
        ) from e

    return [
        LogEntryResponse(
            id=r.id,
            session_id=r.session_id,
            user_message=r.user_message,
            assistant_message=r.assistant_message,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in rows
    ]