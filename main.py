from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi import Query


from database import get_db, engine, Base
from models import ChatLog
from weather_service import get_current_weather

# Ensure tables exist (safe to call on startup)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chat Agent (Weather Tool + DB Logging)")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    # Simple tool-using behavior:
    # If user message starts with "weather:" we call the weather tool.
    text = req.message.strip()

    if text.lower().startswith("weather:"):
        location = text.split(":", 1)[1].strip()
        reply = get_current_weather(location)
    else:
        reply = (
            "Say `weather: <city>` to get current weather. "
            "Example: `weather: Beirut`."
        )

    log = ChatLog(
        session_id=req.session_id,
        user_message=req.message,
        assistant_message=reply,
    )
    db.add(log)
    db.commit()

    return ChatResponse(session_id=req.session_id, reply=reply)
@app.get("/logs/{session_id}")
def get_logs(session_id: str, limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    rows = (
        db.query(ChatLog)
        .filter(ChatLog.session_id == session_id)
        .order_by(ChatLog.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "user_message": r.user_message,
            "assistant_message": r.assistant_message,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
