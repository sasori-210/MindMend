"""
main.py — MindMend chatbot API + web server.

Two endpoints:

  POST /chat/completions   — EXACTLY the Masquerade '26 spec. Untouched
                              request/response shape, always responds in
                              English internally (judging platform doesn't
                              send a language field), so this stays 100%
                              safe for submission no matter what the webapp
                              does.

  POST /api/chat            — richer endpoint for the MindMend webpage.
                               Accepts {message, history, language} and
                               returns {reply, emotion, language}.

  GET  /                    — serves the chat webpage (static/index.html).

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8000

Then open http://localhost:8000 in a browser for the webpage, or submit
the base URL (without /chat/completions) for judging.
"""

import time
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

from engine import generate_reply

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="MindMend Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "mindmend-v1"
    messages: List[ChatMessage]
    stream: Optional[bool] = False


class ApiChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    language: Optional[str] = "en"


def _approx_tokens(text: str) -> int:
    return max(1, len(text.split()))


@app.post("/chat/completions")
async def chat_completions(payload: ChatCompletionRequest):
    """Exact Masquerade '26 spec endpoint. Do not add extra response fields
    here — this must stay parseable by the judging platform exactly as
    documented."""
    messages = [m.model_dump() for m in payload.messages]
    reply_text, _emotion = generate_reply(messages, language="en")

    prompt_tokens = sum(_approx_tokens(m["content"]) for m in messages)
    completion_tokens = _approx_tokens(reply_text)

    response = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": payload.model or "mindmend-v1",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply_text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }
    return JSONResponse(content=response, status_code=200)


@app.post("/api/chat")
async def api_chat(payload: ApiChatRequest):
    """Richer endpoint for the MindMend webpage: includes an emotion tag
    the frontend uses to color/animate the breathing orb, and honors the
    selected language."""
    history = [m.model_dump() for m in (payload.history or [])]
    history.append({"role": "user", "content": payload.message})

    reply_text, emotion = generate_reply(history, language=payload.language)

    return JSONResponse(
        content={
            "reply": reply_text,
            "emotion": emotion,
            "language": payload.language or "en",
        },
        status_code=200,
    )


@app.get("/")
async def index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        content={"status": "ok", "service": "MindMend chatbot", "endpoint": "/chat/completions"}
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MindMend chatbot"}
