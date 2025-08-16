"""Core logic for Illini Prompt Nurse prototype.

This module implements message filtering, crisis detection,
appointment recognition, and triage scoring. Functions are kept
simple and stateless so they can be unit tested.
"""

from __future__ import annotations
from typing import Dict, Any
import re

# Keywords for simple heuristics
IRRELEVANT_PATTERNS = [
    re.compile(r"\b(?:cow|cows|moo)\b", re.IGNORECASE),
]

CRISIS_PATTERNS = [
    re.compile(r"\b(?:suicide|kill myself|don't want to live)\b", re.IGNORECASE),
]

APPOINTMENT_PATTERNS = [
    re.compile(r"\b(?:appointment|schedule|come in)\b", re.IGNORECASE),
]

URGENT_PATTERNS = [
    re.compile(r"\b(?:chest pain|difficulty breathing|shortness of breath)\b", re.IGNORECASE),
]

# Simple in-memory cache. In production this would be persisted or replaced with Redis.
CACHE: Dict[str, Dict[str, Any]] = {}

def is_message_relevant(message: str) -> bool:
    """Return True if the message appears relevant to health triage."""
    return not any(p.search(message) for p in IRRELEVANT_PATTERNS)

def contains_crisis_language(message: str) -> bool:
    """Detect potential mental health crisis language."""
    return any(p.search(message) for p in CRISIS_PATTERNS)

def recognize_appointment_intent(message: str) -> bool:
    """Identify whether the student seems to request an appointment."""
    return any(p.search(message) for p in APPOINTMENT_PATTERNS)

def triage_priority(message: str) -> str:
    """Return 'high' or 'routine' priority based on simple heuristics."""
    return "high" if any(p.search(message) for p in URGENT_PATTERNS) else "routine"

def disclaimer_for(message: str) -> str | None:
    """Return the legal disclaimer if message contains urgent symptoms."""
    if any(p.search(message) for p in URGENT_PATTERNS):
        return (
            "Illini Prompt Nurse is not legally allowed to give medical recommendations. "
            "You must always contact McKinley Health Center for confirmation."
        )
    return None

def sanitize_message(message: str, max_chars: int = 500) -> str:
    """Trim very long messages to save tokens."""
    message = message.strip()
    if len(message) > max_chars:
        return message[:max_chars] + "..."
    return message

def make_cache_key(student_id: str, message: str) -> str:
    """Create a cache key from student ID and message."""
    return f"{student_id}:{message.lower()}"

def generate_stub_response(message: str) -> str:
    """Placeholder for GPT call; returns deterministic stub."""
    if "chest pain" in message.lower():
        return (
            "However, based on the symptoms you’ve described, you might consider "
            "visiting in person if symptoms worsen or persist."
        )
    return "Thanks for your message. A nurse will review your information soon."

def run_gpt(student_id: str, message: str) -> Dict[str, Any]:
    """Process a student message and return a structured response.

    The function applies filtering for irrelevant content, crisis language
    detection, caching, disclaimer injection and simple metadata generation.
    ``confidence`` is a fixed stub value to mimic model output.
    """
    if not is_message_relevant(message):
        return {
            "response": "⚠️ This is not an appropriate question for Illini Prompt Nurse.",
            "priority": "low",
            "confidence": 0,
            "blocked": True,
            "cached": False,
        }

    if contains_crisis_language(message):
        return {
            "response": "Your message has been forwarded to the Mental Health Office for urgent review.",
            "priority": "high",
            "confidence": 100,
            "crisis": True,
            "cached": False,
        }

    key = make_cache_key(student_id, message)
    if key in CACHE:
        cached = CACHE[key].copy()
        cached["cached"] = True
        return cached

    cleaned = sanitize_message(message)
    response_text = generate_stub_response(cleaned)

    if disclaimer := disclaimer_for(cleaned):
        response_text = f"{disclaimer} {response_text}"

    data = {
        "response": response_text,
        "priority": triage_priority(cleaned),
        "confidence": 91,
        "appointment_intent": recognize_appointment_intent(cleaned),
        "cached": False,
    }
    CACHE[key] = data
    return data
