"""FastAPI wrapper for Illini Prompt Nurse prototype."""
from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import os
from typing import Dict

from core import (
    is_message_relevant,
    contains_crisis_language,
    recognize_appointment_intent,
    triage_priority,
    disclaimer_for,
    sanitize_message,
    make_cache_key,
)

app = FastAPI(title="Illini Prompt Nurse")

# Simple in-memory cache and storage
CACHE: Dict[str, Dict[str, str]] = {}
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class MessageRequest(BaseModel):
    student_id: str
    message: str


@app.post("/message")
async def handle_message(req: MessageRequest):
    """Main endpoint for student messages."""
    if not is_message_relevant(req.message):
        return JSONResponse(
            {"response": "⚠️ This is not an appropriate question for Illini Prompt Nurse."},
            status_code=400,
        )

    if contains_crisis_language(req.message):
        # In real system, trigger escalation workflow.
        return JSONResponse(
            {
                "response": "Your message has been forwarded to the Mental Health Office for urgent review.",
                "priority": "high",
            },
            status_code=202,
        )

    key = make_cache_key(req.student_id, req.message)
    if key in CACHE:
        return {"response": CACHE[key]["response"], "cached": True}

    cleaned = sanitize_message(req.message)
    response_text = generate_stub_response(cleaned)

    if disclaimer := disclaimer_for(cleaned):
        response_text = f"{disclaimer} {response_text}"

    CACHE[key] = {"response": response_text}

    data = {
        "response": response_text,
        "priority": triage_priority(cleaned),
        "appointment_intent": recognize_appointment_intent(cleaned),
        "cached": False,
    }
    return data


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept and store uploaded documents."""
    contents = await file.read()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    # Metadata extraction would happen here.
    return {"filename": file.filename, "size": len(contents)}


def generate_stub_response(message: str) -> str:
    """Placeholder for GPT call; returns deterministic stub."""
    # In production this would call OpenAI's API.
    if "chest pain" in message.lower():
        return "However, based on the symptoms you’ve described, you might consider visiting in person if symptoms worsen or persist."
    return "Thanks for your message. A nurse will review your information soon."


@app.get("/")
async def root():
    return {"message": "Illini Prompt Nurse API"}

